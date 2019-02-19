import PIL.Image
import dlib
import numpy as np
import face_recognition_models
import cv2
import time
from pathlib import Path
from filters import *


face_detector = dlib.get_frontal_face_detector()
model_68_points = face_recognition_models.pose_predictor_model_location()
predictor_68_point = dlib.shape_predictor(model_68_points)
face_cascade = cv2.CascadeClassifier(face_recognition_models.haar_cascade_frontal_face_model_location())
eye_cascade = cv2.CascadeClassifier(face_recognition_models.haar_cascade_eye_model_location())


def rect_to_bounds(rect):
    """Extracts bounds of rectangle.

    :param rect: rectangular shape
    :returns: bounds of rect
    """
    return rect.top(), rect.right(), rect.bottom(), rect.left()


def bounds_to_rect(bounds):
    """Creates rectangle from bounds.

    :param bounds: bounds of rectangular shape
    :returns: rectangle
    """
    return dlib.rectangle(bounds[3], bounds[0], bounds[1], bounds[2])


def detect_rect_bounds(bounds, image_shape):
    """Detects bounds of rectangle.

    :param bounds: bounds of rectangular shape
    :param image_shape: shape of image
    :returns: bounds of rectangle
    """
    return max(bounds[0], 0), min(bounds[1], image_shape[1]), min(bounds[2], image_shape[0]), max(bounds[3], 0)


def load_image_file(file):
    """Loads image from file.

    :param file: image file
    :returns: image as numpy array
    """
    im = PIL.Image.open(file)
    im = im.convert('RGB')
    return np.array(im)


def detect_face_location(image, number_of_times=1):
    """Detects faces on image.

    :param image: image with potential faces
    :param number_of_times: number of times to try detecting faces
    :returns: detected faces
    """
    return face_detector(image, number_of_times)


def face_locations(image, number_of_times=1):
    """Detects positions of faces on image.

    :param image: image with potential faces
    :param number_of_times: number of times to try detecting faces
    :returns: list of detected faces
    """
    return [detect_rect_bounds(rect_to_bounds(face), image.shape)
            for face in detect_face_location(image, number_of_times)]


def predict_face_landmarks(face_image, location_of_faces=None,):
    """Predicts landmarks on faces.

    :param face_image: image with faces
    :param location_of_faces: locations of detected faces
    :returns: list of landmarks' locations
    """
    if location_of_faces is None:
        location_of_faces = detect_face_location(face_image)
    else:
        location_of_faces = [bounds_to_rect(face_location) for face_location in location_of_faces]

    return [predictor_68_point(face_image, face_location) for face_location in location_of_faces]


def face_landmarks(face_image, location_of_faces=None):
    """Predicts landmarks on faces.

    :param face_image: image with faces
    :param location_of_faces: locations of detected faces
    :returns: list of dicts from each face's landmarks' locations
    """
    landmarks = predict_face_landmarks(face_image, location_of_faces)
    landmarks_as_tuples = [[(p.x, p.y) for p in landmark.parts()] for landmark in landmarks]
    return [{
        "chin": points[0:17],
        "left_eyebrow": points[17:22],
        "right_eyebrow": points[22:27],
        "nose_bridge": points[27:31],
        "nose_tip": points[31:36],
        "left_eye": points[36:42],
        "right_eye": points[42:48],
        "top_lip": points[48:55] + [points[64]] + [points[63]] + [points[62]] + [points[61]] + [points[60]],
        "bottom_lip": points[54:60] + [points[48]] + [points[60]] +
                      [points[67]] + [points[66]] + [points[65]] + [points[64]]
    } for points in landmarks_as_tuples]


def detect_dlib(img, faces_number, draw_rectangles, chosen_filter, intersections):
    """Detects faces using dlib library.

    :param img: frame
    :param faces_number: number of expected faces in frame
    :param draw_rectangles: indicator whether rectangles that bound detected faces and 68 points should be drawn
    :param chosen_filter: chosen filter that is attached to detected faces
    :param intersections: list of intersections for frames
    :returns: result image and indicator that tells if correct number of faces is detected
    """
    faces = face_locations(img, number_of_times=1)
    face_landmarks_list = face_landmarks(img, faces)

    if draw_rectangles:
        for idx, located_face in enumerate(faces):
            face = bounds_to_rect(located_face)
            x = face.left()
            y = face.top()
            w = face.right() - x
            h = face.bottom() - y
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

            f = face_landmarks_list[idx]  # landmarks that belong to face
            for key, value in f.items():
                for i in value:
                    try:
                        img[i[1]][i[0]] = (0, 0, 255)
                    except:
                        pass

    if chosen_filter != "":
        frame_intersections = []
        for idx, face in enumerate(faces):      # attach filter to each face
            put_filter_on(img, face, face_landmarks_list[idx], chosen_filter, frame_intersections)
        if len(frame_intersections) > 0:
            inters = sum(frame_intersections) / len(frame_intersections)    # average intersection for frame
            intersections.append(inters)

    if faces_number == -1:
        return img, True
    else:
        return img, len(faces) == faces_number


def detect_cv(f, faces_number, draw_rectangles):
    """Detects faces using opencv library.

    :param f: frame
    :param faces_number: number of expected faces in frame
    :param draw_rectangles: indicator whether rectangles that bound detected faces should be drawn
    :returns: result image and indicator that tells if correct number of faces is detected
    """
    gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    # eyes = eye_cascade.detectMultiScale(f)
    if draw_rectangles:
        for (x, y, w, h) in faces:
            cv2.rectangle(f, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # for (ex, ey, ew, eh) in eyes:
            #     cv2.rectangle(f, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

    if faces_number == -1:
        return f, True
    else:
        return f, len(faces) == faces_number


def generate_output_path(path, chosen_filter):
    """Generates file path for output result video.

    :param path: input path
    :param chosen_filter: chosen filter that is attached to detected faces
    :returns: path of output file
    """
    tokens = path.split("/")
    output_path = ""
    for i in range(0, len(tokens) - 1):
        output_path += tokens[i] + "/"

    line = "_"
    if chosen_filter == "":
        line = ""   # no filter chosen
    result_path = output_path + "result_video" + line + chosen_filter + ".avi"
    my_file = Path(result_path)
    counter = 1
    while my_file.is_file():    # if file exists generate new path
        result_path = output_path + "result_video_" + chosen_filter + "(" + str(counter) + ").avi"
        my_file = Path(result_path)
        counter += 1
    return result_path


def process_video(path, faces_number, draw_rectangles, chosen_filter, window):
    """Processes input video frame by frame and shows result video.

    :param path: path of input file
    :param faces_number: number of expected faces in frame
    :param draw_rectangles: indicator whether rectangles that bound detected faces should be drawn
    :param chosen_filter: chosen filter that is attached to detected faces
    :param window: main window that is used for interaction with user
    :returns: indicator for detection success
    """
    start = time.time()
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print("Error opening video!")
        return False
    result = []         # list of result frames
    intersections = []  # list of intersections for each frame
    frame_counter = 0   # coutner of frames
    dlib_true_counter = 0   # counter for frames with valid number of detected faces by dlib
    cv_true_counter = 0     # counter for frames with valid number of detected faces by opencv
    output_path = generate_output_path(path, chosen_filter)     # generate result video path
    fps = cap.get(cv2.CAP_PROP_FPS)     # video fps
    width = int(cap.get(3))             # video width
    height = int(cap.get(4))            # video height
    result_video_writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), fps, (width, height))
    try:
        while cap.isOpened():
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret:
                frame_counter += 1

                image, res = detect_dlib(frame, faces_number, draw_rectangles, chosen_filter, intersections)
                if res:
                    dlib_true_counter += 1

                print("Processed frame " + str(frame_counter) + " with dlib!")
                image, res = detect_cv(image, faces_number, draw_rectangles)
                if res:
                    cv_true_counter += 1
                print("Processed frame " + str(frame_counter) + " with opencv!")

                result.append(image)
                result_video_writer.write(image)    # write result video
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            else:
                break
    except:
        pass

    cap.release()
    result_video_writer.release()
    cv2.destroyAllWindows()
    print("Processing phase is done! Time elapsed: " + str(time.time() - start) + "!")
    if faces_number != -1:
        print("Detection success with dlib: " + str(round(dlib_true_counter / frame_counter * 100, 2)) + " %!")
        print("Detection success with opencv: " + str(round(cv_true_counter / frame_counter * 100, 2)) + " %!")
        if len(intersections) != 0:
            print("Detection success (Intersection over Union - IoU): "
                  + str(round(sum(intersections) / len(intersections) * 100, 2)) + " %!")
        else:
            print("Detection success (Intersection over Union - IoU): 0%!")

    # showing result
    result_cap = cv2.VideoCapture(path)
    if not result_cap.isOpened():
        print("Error opening video!")
        return False
    window.hide()
    frame_counter = 0
    try:
        while result_cap.isOpened():
            # Capture frame-by-frame
            ret, frame = result_cap.read()
            if ret:
                # Display the resulting frame
                cv2.imshow('Frame', (result[frame_counter]))
                frame_counter += 1
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            else:
                break
    except:
        pass
    result_cap.release()
    cv2.destroyAllWindows()
    window.show()
    return True