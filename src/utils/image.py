import base64
import cv2
from werkzeug.datastructures import FileStorage
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark
from mediapipe.python.solutions.drawing_utils import draw_landmarks
from mediapipe.framework.formats import landmark_pb2
import numpy as np


def decode_image(file: FileStorage):
    file_bytes = np.fromfile(file, np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    return image


def get_annotation(image, pose_landmark_list: list[list[NormalizedLandmark]]):
    annotated_image = np.copy(image)

    # Loop through the detected poses to visualize.
    for idx in range(len(pose_landmark_list)):
        pose_landmarks = pose_landmark_list[idx]

        # Generate pose landmarks list.
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        pose_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
        ])

        pose_connection = frozenset({
            (30, 28), (28, 26), (26, 24), (24, 12), (12, 5), (5, 33)
        })

        # Draw landmarks and line
        draw_landmarks(
            annotated_image,
            pose_landmarks_proto,
            pose_connection,
        )

    return annotated_image


def resize_image(image):
    h, w, *_ = image.shape
    nw = 500
    nh = int(nw * h / w)
    resized_image = cv2.resize(image, (nw, nh))
    return resized_image


def encode_image(image):
    encode_params = [int(cv2.IMWRITE_PNG_COMPRESSION), 9]
    _, buffer = cv2.imencode('.png', image, encode_params)
    encoded_image = base64.b64encode(buffer).decode('ascii')
    return encoded_image
