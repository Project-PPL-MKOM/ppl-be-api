from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarkerOptions, PoseLandmarker
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark
from mediapipe import Image, ImageFormat
import numpy as np
import os


def detect_pose_landmarks(image) -> list[list[NormalizedLandmark]]:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    asset_path = os.path.join(dir_path, 'pose_landmarker.task')
    base_options = BaseOptions(model_asset_path=asset_path)
    options = PoseLandmarkerOptions(base_options=base_options)
    detector = PoseLandmarker.create_from_options(options)

    img = Image(image_format=ImageFormat.SRGB, data=image)
    detection_result = detector.detect(img)
    return detection_result.pose_landmarks


def adjust_shoulder(pose_landmark: list[NormalizedLandmark]):
    L = np.array([pose_landmark[11].x, pose_landmark[11].y])
    R = np.array([pose_landmark[12].x, pose_landmark[12].y])
    delta = (R - L) * 0.2
    L += delta
    R -= delta
    pose_landmark[11].x = L[0]
    pose_landmark[11].y = L[1]
    pose_landmark[12].x = R[0]
    pose_landmark[12].y = R[1]
    return pose_landmark


def set_topmost_point(pose_landmark: list[NormalizedLandmark]):
    nose = np.array([pose_landmark[5].x, pose_landmark[5].y])
    shoulder = np.array([pose_landmark[12].x, pose_landmark[12].y])
    hip = np.array([pose_landmark[24].x, pose_landmark[24].y])

    facial_dist = np.linalg.norm(shoulder - nose) * 0.925
    body = shoulder - hip
    body_unit = body / np.linalg.norm(body)
    topmost_loc = nose + facial_dist * body_unit

    pose_landmark.append(
        NormalizedLandmark(
            x=topmost_loc[0], y=topmost_loc[1], z=pose_landmark[5].z)
    )
    return pose_landmark


def get_connection_length(pose_landmark: list[NormalizedLandmark]):
    pose_connection = frozenset({
        (30, 28), (28, 26), (26, 24), (24, 12), (12, 5), (5, 33)
    })

    # Iterate through each connection
    total_length: float = 0.0
    for connection in pose_connection:
        p_start, p_end = connection
        vec_start = np.array(
            [pose_landmark[p_start].x, pose_landmark[p_start].y])
        vec_end = np.array(
            [pose_landmark[p_end].x, pose_landmark[p_end].y])
        total_length += np.linalg.norm(vec_end - vec_start)

    return total_length
