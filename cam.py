import cv2
from pathlib import Path


def generate_path(path):
    """ Generates path for the result video - video that
        contains sticker. If file with created name already
        exists on the system then to the path is being added
        counter value (number).

    :param path: path to the file
    :return: result path for the result video
    """
    tokens = path.split("/")
    output_path = ""
    for i in range(0, len(tokens) - 1):
        output_path += tokens[i] + "/"

    result_path = output_path + "output_video" + ".avi"
    my_file = Path(result_path)
    counter = 1
    while my_file.is_file():
        result_path = output_path + "output_video" + "(" + str(counter) + ").avi"
        my_file = Path(result_path)
        counter += 1
    return result_path


def record_from_camera(path, window):
    """ Method used for recording video from camera.
        Recorded video is being saved in .avi format
        on the system.

    :param path: path to the file
    :param window: main window instance
    :return: path to recorded video
    """
    window.hide()
    output_path = generate_path(path)  # generate output video path
    try:
        cam = cv2.VideoCapture(0)
        video_writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc('M','J','P','G'), 10, (640, 480))

        frame_counter = 0
        while cam.isOpened():
            ret, frame = cam.read()
            if ret:
                frame = cv2.flip(frame, 1)
                # write the flipped frame

                if (160 - frame_counter) % 32 == 0 and frame_counter <= 160:
                    if frame_counter == 160:
                        print("Recording started!")
                    else:
                        print("Recording starting in " + str(int((160 - frame_counter) / 32)) + " seconds!")

                if frame_counter >= 160:
                    video_writer.write(frame)

                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                if frame_counter >= 320:
                    break
                frame_counter += 1
            else:
                break

        cam.release()
        video_writer.release()
        cv2.destroyAllWindows()
    except:
        pass
    window.show()
    return output_path