import math
import cv2
from imutils import rotate_bound
from detection import *
import numpy as np


def calculate_angle(point1, point2):
    """ Calculates angle between to points.
        Point1 belongs to left and point2 to
        right eyebrow.

    :param point1: [x1, y1] contains coordinates of the point
    :param point2: [x2, y2] contains coordinates of the point
    :return: float value of the angle between two points
    """
    x1, x2, y1, y2 = point1[0], point2[0], point1[1], point2[1]
    return 180 / math.pi * math.atan((float(y2 - y1)) / (x2 - x1))


def get_bound_box(points):
    """ Calculates bound box around points.


    :param points: list of points (x, y) that represent some
    of face parts like left eye, one of the eyebrows, etc.
    :return: min_x - x coordinate of the upper left corner
    for bounding box around points
             min_y - y coordinate of the upper left corner
    for bounding box around points
             width, height - dimensions of the bounding box
    """
    min_x = 99999
    min_y = 99999
    max_x = -99999
    max_y = -99999
    for p in points:
        if p[0] > max_x:
            max_x = p[0]
        if p[0] < min_x:
            min_x = p[0]
        if p[1] > max_y:
            max_y = p[1]
        if p[1] < min_y:
            min_y = p[1]
    width = max_x - min_x
    height = max_y - min_y
    return min_x, min_y, width, height


def face_part(points, face_part):
    """ Calls method for calculating bounding box for points
    around points, based on face part needed.

    :param points: dictionary that for every key (face part name) contains
            list of points
    :param face_part: string key for getting points for exact face part
    :return: values that get_bound_box returns
             x, y - coordinates of upper left corner of the bounding box
             width, height - dimensions of the bounding box.
    """
    if face_part == "left_eye":
        x, y, w, h = get_bound_box(points["left_eye"])
        return x, y, w, h
    elif face_part == "right_eye":
        x, y, w, h = get_bound_box(points["right_eye"])
        return x, y, w, h
    elif face_part == "left_eyebrow":
        x, y, w, h = get_bound_box(points["left_eyebrow"])
        return x, y, w, h
    elif face_part == "top_lip":
        x, y, w, h = get_bound_box(points["top_lip"])
        return x, y, w, h
    elif face_part == "nose_tip":
        x, y, w, h = get_bound_box(points["nose_tip"])
        return x, y, w, h
    elif face_part == "bottom_lip":
        x, y, w, h = get_bound_box(points["bottom_lip"])
        return x, y, w, h
    elif face_part == "nose_bridge":
        x, y, w, h = get_bound_box(points["nose_bridge"])
        return x, y, w, h


def add_sticker(image, sticker, cor_x, cor_y, face_land, face, sticker_path):
    """ Adds sticker to the video frame.

    :param image: frame from the video
    :param sticker: sticker image that is being added to the frame
    :param cor_x: x coordinate where sticker needs to be added (upper left corner)
    :param cor_y: y coordinate where sticker needs to be added (upper left corner)
    :param face_land: dictionary of points for face parts
    :param face: rectangle around face from the frame
    :param sticker_path: path to the sticker image
    :return: image - newly created image with sticker on it
             inter - intersection over union coefficient that returns
             method check_intersections called from this method
    """
    image_height, image_width = image.shape[0], image.shape[1]
    s_height, s_width = sticker.shape[0], sticker.shape[1]

    # if sticker goes out of image in the bottom
    if cor_y + s_height >= image_height:
        sticker = sticker[0:image_height - cor_y, :, :]

    # if sticker goes out of image in the right
    if cor_x + s_width >= image_width:
        sticker = sticker[:, 0:image_width - cor_x, :]

    # if sticker goes out of image on the left
    if cor_x < 0:
        sticker = sticker[:, abs(cor_x)::, :]
        cor_x = 0
        s_width = sticker.shape[0]

    if cor_x < 0:
        cor_x = 0
    if cor_y < 0:
        cor_y = 0
    # RGB -> 3 channels
    for chanel in range(3):
        image[cor_y:cor_y + s_height, cor_x:cor_x + s_width, chanel] = \
            sticker[:, :, chanel] * (sticker[:, :, 3] / 255.0) + \
            image[cor_y:cor_y + s_height, cor_x:cor_x + s_width, chanel] \
            * (1.0 - sticker[:, :, 3] / 255.0)
    w_temp, h = sticker.shape[1], sticker.shape[0]
    inter = check_intersections(sticker_path, h, w_temp, cor_y, cor_x, face_land, face)
    if inter is None:
        inter = 0
    return image, inter


def adjust_sticker(image, sticker_path, angle, face_width, face_y, face_x, face_land, face):
    """ Method adjusts sticker image to the frame, sticker
        is being resized for face dimensions and
        rotated based on the angle provided as
        parameter.

    :param image: frame from the video
    :param sticker_path: path to the sticker image
    :param angle: angle of rotation
    :param face_width: width of the rectangle around face
    :param face_y: y coordinate of the upper left corner of the rectangle around face
    :param face_x: x coordinate of the upper left corner of the rectangle around face
    :param face_land: dictionary of points for face parts
    :param face: rectangle around face
    :return: calls method add_sticker for adding sticker on the frame, and returns
             return values from that method
    """
    sticker = cv2.imread(sticker_path, -1)
    rotated = rotate_bound(sticker, angle)

    s_width, s_height = rotated.shape[1], rotated.shape[0]
    dv = face_width / s_width

    rotated = cv2.resize(rotated, (0, 0), fx=dv, fy=dv)  # resize width to be same as face width
    s_width, s_height = rotated.shape[1], rotated.shape[0]  # new width, height after resize

    if sticker_path == "stickers/mustache.png":
        face_x = int(face_x - s_width / 2)
    return add_sticker(image, rotated, face_x, face_y, face_land, face, sticker_path)


# get height between the open lips
def check_if_mouth_open(points):
    """ Checks if mouth of the face in the frame is open.
        Condition if the mouth is open is based on whether
        it is the size of the hatch between top and bottom
        lip bigger than half width of the bottom lip.

    :param points: dictionary of points for face parts
    :return: boolean value True - if the condition is met
             else False
    """
    middle_points = []
    middle_points.append(points["top_lip"][6])
    middle_points.append(points["top_lip"][7])
    middle_points.append(points["top_lip"][8])

    middle_points.append(points["bottom_lip"][len(points["bottom_lip"]) - 2])
    middle_points.append(points["bottom_lip"][len(points["bottom_lip"]) - 3])
    middle_points.append(points["bottom_lip"][len(points["bottom_lip"]) - 4])

    min_x, min_y, w, h = get_bound_box(middle_points)
    x, y, w_bottom_lip, h_bottom_lip = face_part(points, "bottom_lip")

    if h > h_bottom_lip / 2:
        return True
    return False


def put_filter_on(image, face, face_land, sticker_name, intersections):
    """ Method is used as dispatcher function based on sticker name
        and calls method for adjusting sticker and indirectly adding
        sticker on the frame and calculating intersection coefficient
        and adding it to the intersections list.

    :param image: frame from the video
    :param face: rectangle around the face from the frame
    :param face_land: dictionary of points for face parts
    :param sticker_name: name of the chosen sticker
    :param intersections: list in which calculated iou coefficient
           is being inserted
    :return: no return value cause image and intersections are sent
             as parameters over reference
    """
    if sticker_name != "":
        face = dlib.rectangle(face[3], face[0], face[1], face[2])
        x = face.left()
        y = face.top()
        w = face.right() - x
        h = face.bottom() - y
        ang = calculate_angle(face_land["left_eyebrow"][0], face_land["right_eyebrow"][-1])
        sticker_path = ""
        if sticker_name == "cat":
            x1, y1, w1, h1 = face_part(face_land, "left_eyebrow")
            sticker_path += "stickers/cat.png"
            y_temp = int(max(min(y - h / 2, y1 - h / 2), 0))
            x_temp = max(min(x, x1), 0)
            image, inter = adjust_sticker(image, sticker_path, ang, w, y_temp, x_temp, face_land, face)
            intersections.append(inter)
        elif sticker_name == "ears":
            x1, y1, w1, h1 = face_part(face_land, "left_eyebrow")
            sticker_path += "stickers/ears.png"
            y_temp = int(max(min(y - h / 2, y1 - h / 2 - h / 8), 0))
            x_temp = int(max(min(x, x1) - w / 8, 0))
            w_temp = int(w + w / 4)
            image, inter = adjust_sticker(image, sticker_path, ang, w_temp, y_temp, x_temp, face_land, face)
            intersections.append(inter)
        elif sticker_name == "flowers":
            sticker_path += "stickers/flowers.png"
            y_temp = int(max(y - h / 2 - h / 8, 0))
            x_temp = int(x - w / 8)
            w_temp = int(w + w / 4)
            image, inter = adjust_sticker(image, sticker_path, ang, w_temp, y_temp, x_temp, face_land, face)
            intersections.append(inter)
        elif sticker_name == "glasses":
            x1, y1, w1, h1 = face_part(face_land, "left_eyebrow")
            sticker_path += "stickers/glasses.png"
            y_temp = max(min(y, y1), 0)
            x_temp = max(min(x, x1), 0)
            image, inter = adjust_sticker(image, sticker_path, ang, w, y_temp, x_temp, face_land, face)
            intersections.append(inter)
        elif sticker_name == "mask":
            x1, y1, w1, h1 = face_part(face_land, "left_eyebrow")
            sticker_path += "stickers/mask.png"
            y_temp = max(min(y, y1), 0)
            x_temp = max(min(x, x1), 0)
            image, inter = adjust_sticker(image, sticker_path, ang, w, y_temp, x_temp, face_land, face)
            intersections.append(inter)
        elif sticker_name == "mustache":
            x1, y1, w1, h1 = face_part(face_land, "nose_tip")
            sticker_path += "stickers/mustache.png"
            x_temp = int(x1 + w1 / 2)
            image, inter = adjust_sticker(image, sticker_path, ang, w, y1, x_temp, face_land, face)
            intersections.append(inter)
        elif sticker_name == "mouse":
            x1, y1, w1, h1 = face_part(face_land, "left_eyebrow")
            sticker_path += "stickers/mouse.png"
            y_temp = int(max(min(y - h / 4, y1 - h / 4) - h / 6, 0))
            x_temp = max(int(min(x, x1) - w / 8), 0)
            w_temp = int(w + w / 4)
            image, inter = adjust_sticker(image, sticker_path, ang, w_temp, y_temp, x_temp, face_land, face)
            intersections.append(inter)
        elif sticker_name == "pirate":
            sticker_path += "stickers/pirate.png"
            w_temp = int(w + w / 8)
            y_temp = int(max(y - h / 2, 0))
            x_temp = max(int(x - w / 16), 0)
            image, inter = adjust_sticker(image, sticker_path, ang, w_temp, y_temp, x_temp, face_land, face)
            intersections.append(inter)
        elif sticker_name == "rainbow":
            mouth_open = check_if_mouth_open(face_land)
            if mouth_open:
                x1, y1, w1, h1 = face_part(face_land, "top_lip")
                sticker_path += "stickers/rainbow.png"
                w_temp = int(w + w / 4)
                y_temp = max(0, int(y1 - h / 8))
                x_temp = max(int(min(x, x1) - w / 8), 0)
                image, inter = adjust_sticker(image, sticker_path, ang, w_temp, y_temp, x_temp, face_land, face)
                intersections.append(inter)


def check_intersections(sticker_path, h, w, y, x, face_land, face):
    """ Calls get_iou method for calculating iou coefficient for
        one or more face parts and returns avg of them.

    :param sticker_path: path to the sticker image
    :param h: sticker height
    :param w: sticker width
    :param y: coordinate of the upper left corner where sticker is being added
    :param x: coordinate of the upper left corner where sticker is being added
    :param face_land: dictionary of points for face parts
    :param face: rectangle around the face from the frame
    :return: iou coefficient (if it is called for more than one face part then
             avg of those iou coefficients for those parts)
    """
    if "mask" in sticker_path or "glasses" in sticker_path:
        x1, y1, w1, h1 = face_part(face_land, "left_eye")
        x2, y2, w2, h2 = face_part(face_land, "right_eye")
        coef_left = get_iou(x1, y1, w1, h1, x, y, w, h)
        coef_right = get_iou(x2, y2, w2, h2, x, y, w, h)
        return (coef_left + coef_right) / 2
    elif "mustache" in sticker_path:
        x1, y1, w1, h1 = face_part(face_land, "top_lip")
        return get_iou(x1, y1, w1, h1, x, y, w, h)
    elif "rainbow" in sticker_path:
        x1, y1, w1, h1 = face_part(face_land, "top_lip")
        x2, y2, w2, h2 = face_part(face_land, "bottom_lip")
        coef_top = get_iou(x1, y1, w1, h1, x, y, w, h)
        coef_bottom = get_iou(x2, y2, w2, h2, x, y, w, h)
        return (coef_top + coef_bottom) / 2
    elif "mouse" in sticker_path:
        x1, y1, w1, h1 = face_part(face_land, "nose_bridge")
        if w1 == 0:
            w1 = 1
        coef_nose_bridge = get_iou(x1, y1, w1, h1, x, y, w, h)
        x1, y1, w1, h1 = face_part(face_land, "left_eye")
        coef_left_eye = get_iou(x1, y1, w1, h1, x, y, w, h)
        x1, y1, w1, h1 = face_part(face_land, "right_eye")
        coef_right_eye = get_iou(x1, y1, w1, h1, x, y, w, h)
        return (coef_nose_bridge + coef_left_eye + coef_right_eye) / 3
    elif "cat" in sticker_path:
        x1, y1, w1, h1 = face_part(face_land, "nose_bridge")
        if w1 == 0:
            w1 = 1
        coef_nose_bridge = get_iou(x1, y1, w1, h1, x, y, w, h)
        x1, y1, w1, h1 = face_part(face_land, "nose_tip")
        coef_nose_tip = get_iou(x1, y1, w1, h1, x, y, w, h)
        x1, y1, w1, h1 = face_part(face_land, "left_eye")
        coef_left_eye = get_iou(x1, y1, w1, h1, x, y, w, h)
        x1, y1, w1, h1 = face_part(face_land, "right_eye")
        coef_right_eye = get_iou(x1, y1, w1, h1, x, y, w, h)
        return (coef_nose_bridge + coef_nose_tip + coef_left_eye + coef_right_eye) / 4
    elif "flowers" in sticker_path or "pirate" in sticker_path or "ears" in sticker_path:
        x1 = face.left()
        y1 = face.top()
        w1 = face.right() - x1
        h1 = face.bottom() - y1
        y_top_left = max(0, int(y1 - h1 / 3.5))
        h_final = int(y1 - y_top_left)
        return get_iou(x1, y_top_left, w1, h_final, x, y, w, h)


def get_iou(x1, y1, w1, h1, x_sticker, y_sticker, w_sticker, h_sticker):
    """ Calculates Intersection over Union (IoU) coefficient for two
        rectangles. Between rectangle that contains face and rectangle
        that contains sticker.

    :param x1: coordinate of the upper left corner of the face
    :param y1: coordinate of the upper left corner of the face
    :param w1: width of the face
    :param h1: height of the face
    :param x_sticker: coordinate of the upper left corner of the sticker
    :param y_sticker: coordinate of the upper left corner of the sticker
    :param w_sticker: width of the sticker
    :param h_sticker: height of the sticker
    :return: iou coefficient
    """

    # boxes contain 4 numbers [x1,y1,x2,y2]:
    #    x1, y1 - upper left corner
    #    x2, y2 - lower right corner
    box_face = [x1, y1, w1 + x1, h1 + y1]
    box_sticker = [x_sticker, y_sticker, w_sticker + x_sticker, h_sticker + y_sticker]
    if box_sticker[0] < box_face[0] and box_sticker[2] > box_face[0]:
        box_sticker[0] = box_face[0]
    if box_sticker[2] > box_face[2] and box_sticker[0] < box_face[2]:
        box_sticker[2] = box_face[2]

    if box_sticker[1] < box_face[1] and box_sticker[3] > box_face[1]:
        box_sticker[1] = box_face[1]
    if box_sticker[3] > box_face[3] and box_sticker[1] < box_face[3]:
        box_sticker[3] = box_face[3]
    x1 = max(box_face[0], box_sticker[0])
    y1 = max(box_face[1], box_sticker[1])
    x2 = min(box_face[2], box_sticker[2])
    y2 = min(box_face[3], box_sticker[3])

    # overlap area
    width = (x2 - x1)
    height = (y2 - y1)

    # handle no overlap
    if (width < 0) or (height < 0):
        return 0.0
    area_overlap = width * height

    # combined area
    area_face = (box_face[2] - box_face[0]) * (box_face[3] - box_face[1])
    area_sticker = (box_sticker[2] - box_sticker[0]) * (box_sticker[3] - box_sticker[1])
    area_combined = area_face + area_sticker - area_overlap

    if area_combined != 0:
        return area_overlap / area_combined
    else:  # prevent division by zero
        return area_overlap / (area_combined + 1e-5)