import os
from flask import Flask, request, send_file
from utils.image import decode_image, get_annotation
from utils.landmark import detect_pose_landmarks, adjust_shoulder, set_topmost_point, get_connection_length
from utils.response import ResponseBuilder
from utils.validator import validate_request

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 megabytes


@app.route('/')
def index():
    return send_file('index.html')


@app.route("/detect", methods=['POST'])
def detect():
    error_response = validate_request()
    if error_response:
        return error_response, 400

    file = request.files['photo']
    refLength = float(request.form['refLength'])

    image = decode_image(file)
    pose_landmark_list = detect_pose_landmarks(image)
    if len(pose_landmark_list) == 0:
        return ResponseBuilder.failed('Nothing detected').json, 404

    pose_landmark_list = [
        set_topmost_point(adjust_shoulder(pose_landmark)) for pose_landmark in pose_landmark_list
    ]

    # TODO: send annotation image
    annotation_image = get_annotation(image, pose_landmark_list)
    # TODO: do something with vector lengths
    vec_lengths = [
        get_connection_length(pose_landmark) for pose_landmark in pose_landmark_list
    ]

    data = {
        'height': vec_lengths[0]
    }
    return ResponseBuilder.success(data).json, 200

    # TODO: extract reference object and calculate height
    #     # STEP 6: Calculate length
    #     highlighted_image = image.copy()
    #     hsv_image = cv2.cvtColor(highlighted_image, cv2.COLOR_BGR2HSV)
    #     lower_green = np.array([40, 40, 40])
    #     upper_green = np.array([70, 255, 255])
    #      mask = cv2.inRange(hsv_image, lower_green, upper_green)

    #       # Find contours in the thresholded image
    #       contours, _ = cv2.findContours(
    #            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #        # Find the contour corresponding to the first green line
    #        if contours:
    #             first_contour = contours[0]
    #             # Calculate the length of the contour
    #             length = cv2.arcLength(first_contour, closed=True) / \
    #                 annotated_image.shape[0]
    #             print("Panjang vector garis hijau: ", length)
    #             print("Panjang vector bayi: ", heights[0])
    #             print("TINGGI BADAN BAYI: ",
    #                   (500 * heights[0]) / length / 10, " cm")

    #             # Draw the contour on the highlighted image
    #             cv2.drawContours(annotated_image, [
    #                              first_contour], -1, (0, 0, 255), 2)

    #         else:
    #             print("No green line found in the image.")

    #         resized_image = cv2.resize(annotated_image, (500, int(
    #             annotated_image.shape[0] * (500 / annotated_image.shape[1]))))
    #         # cv2_imshow(resized_image)
    #         cv2_imshow(cv2.cvtColor(resized_image, cv2.COLOR_RGB2BGR))

    #         results = pose.process(image)
    #         # Do something with the results, e.g., draw the pose landmarks on the image.
    #         return send_file('processed_image.jpg')


def main():
    # app.run(port=int(os.environ.get('PORT', 3000)))
    app.run()


if __name__ == "__main__":
    main()
