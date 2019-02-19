from pkg_resources import resource_filename


def pose_predictor_model_location():
    return resource_filename(__name__, "models/shape_predictor_68_face_landmarks.dat")
    # return resource_filename(__name__, "models/shape_predictor_5_face_landmarks.dat")


def face_recognition_model_location():
    return resource_filename(__name__, "models/dlib_face_recognition_resnet_model_v1.dat")


def haar_cascade_frontal_face_model_location():
    return resource_filename(__name__, "models/haarcascade_frontalface_default.xml")
    # return resource_filename(__name__, "models/lbpcascade_frontalface_default.xml")


def haar_cascade_eye_model_location():
    return resource_filename(__name__, "models/haarcascade_eye.xml")
