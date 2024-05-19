import os
import base64
import mediapipe as mp

from flask import Flask, request, send_file

from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import cv2

app = Flask(__name__)
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)

@app.route("/")
def index():
    return send_file('index.html')

@app.route("/detect", methods=["GET"])
def detect():
    image_base64 = request.form["image"]
    image_bytes = base64.b64decode(image_base64)
    image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    


    # STEP 1: Import the necessary modules.
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

    # STEP 2: Create an PoseLandmarker object.
    base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=True)
    detector = vision.PoseLandmarker.create_from_options(options)

    # STEP 3: Load the input image.
    image = mp.Image.create_from_file("image.jpg")

    # STEP 4: Detect pose landmarks from the input image.
    detection_result = detector.detect(image)

    # STEP 5: Process the detection result. In this case, visualize it.
    annotated_image, heights = draw_landmarks_on_image(image.numpy_view(), detection_result)

    # STEP 6: Calculate length
    highlighted_image = annotated_image.copy()

    # Convert image to HSV color space
    hsv = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2HSV)

    # Define lower and upper bounds for green color in HSV
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([70, 255, 255])

    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the contour corresponding to the first green line
    if contours:
            first_contour = contours[0]
            # Calculate the length of the contour
            length = cv2.arcLength(first_contour, closed=True) / annotated_image.shape[0]
            print("Panjang vector garis hijau: ", length)
            print("Panjang vector bayi: ", heights[0])
            print("TINGGI BADAN BAYI: ", (500 * heights[0]) / length / 10, " cm")

            # Draw the contour on the highlighted image
            cv2.drawContours(annotated_image, [first_contour], -1, (0, 0, 255), 2)
        
    else:
        print("No green line found in the image.")

    resized_image = cv2.resize(annotated_image, (500, int(annotated_image.shape[0] * (500 / annotated_image.shape[1]))))
    # cv2_imshow(resized_image)
    cv2_imshow(cv2.cvtColor(resized_image, cv2.COLOR_RGB2BGR))



    results = pose.process(image)
    # Do something with the results, e.g., draw the pose landmarks on the image.
    return send_file('processed_image.jpg')

def main():
    app.run(port=int(os.environ.get('PORT', 80)))

if __name__ == "__main__":
    main()




def draw_landmarks_on_image(rgb_image, detection_result):
  pose_landmarks_list = detection_result.pose_landmarks
  annotated_image = np.copy(rgb_image)
  heights = []

  # Loop through the detected poses to visualize.
  for idx in range(len(pose_landmarks_list)):
    pose_landmarks = pose_landmarks_list[idx]

    # Draw the pose landmarks.
    pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    pose_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
    ])

    # Kalibrasi
    a = np.array([pose_landmarks_proto.landmark[11].x, pose_landmarks_proto.landmark[11].y])
    b = np.array([pose_landmarks_proto.landmark[12].x, pose_landmarks_proto.landmark[12].y])
    vector_ab = b - a
    scaled_vector = vector_ab * 0.2
    new_a = a + scaled_vector
    new_b = b - scaled_vector
    pose_landmarks_proto.landmark[11].x = new_a[0]
    pose_landmarks_proto.landmark[11].y = new_a[1]
    pose_landmarks_proto.landmark[12].x = new_b[0]
    pose_landmarks_proto.landmark[12].y = new_b[1]
    a = np.array([pose_landmarks_proto.landmark[5].x, pose_landmarks_proto.landmark[5].y])
    b = np.array([pose_landmarks_proto.landmark[12].x, pose_landmarks_proto.landmark[12].y])
    c = np.array([pose_landmarks_proto.landmark[24].x, pose_landmarks_proto.landmark[24].y])
    vec_cb = b - c
    angle_cb_xaxis = np.arctan2(vec_cb[1], vec_cb[0])
    vec_ab = b - a
    length_ab = np.linalg.norm(vec_ab)
    length_d = 0.925 * length_ab
    d_x = a[0] + length_d * np.cos(angle_cb_xaxis)
    d_y = a[1] + length_d * np.sin(angle_cb_xaxis)
    d = np.array([d_x, d_y])
    pose_landmarks_proto.landmark.append(
      landmark_pb2.NormalizedLandmark(x=d[0], y=d[1], z=pose_landmarks_proto.landmark[5].z)
    )
    
    pose_connection = frozenset({(30,28), (28,26), (26,24), (24,12), (12, 5), (5, 33)})

    solutions.drawing_utils.draw_landmarks(
      annotated_image,
      pose_landmarks_proto,
      pose_connection,
      # solutions.pose.POSE_CONNECTIONS,
      # solutions.drawing_styles.get_default_pose_landmarks_style())
    )

    # Iterate through each connection
    length = 0
    for connection in pose_connection:
      landmark_idx1, landmark_idx2 = connection
      landmark1 = np.array([pose_landmarks_proto.landmark[landmark_idx1].x, pose_landmarks_proto.landmark[landmark_idx1].y])
      landmark2 = np.array([pose_landmarks_proto.landmark[landmark_idx2].x, pose_landmarks_proto.landmark[landmark_idx2].y])
      vector = landmark2 - landmark1
      length += np.linalg.norm(vector)
    heights.append(length)

    
  return annotated_image, heights