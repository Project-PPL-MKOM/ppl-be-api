from dotenv import load_dotenv
from werkzeug.serving import WSGIRequestHandler
from flask import Flask, request
from utils.image import decode_image, encode_image, get_annotation, resize_image
from utils.landmark import detect_pose_landmarks, adjust_shoulder, set_topmost_point, get_connection_length
from utils.response import ResponseBuilder
from utils.ref_obj import detect_ref_obj, get_contour_length
from utils.validator import validate_request
import error_handler

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 megabytes

app.register_blueprint(error_handler.blueprint)


@app.route('/')
def index():
    return ResponseBuilder.success('Hello worldxxx').json, 200
    # return send_file('index.html')


@app.route('/test', methods=['POST'])
def test_upload():
    error_response = validate_request()
    if error_response:
        return error_response, 400
    return ResponseBuilder.success('Hello test').json, 200
    # return send_file('index.html')


@app.route("/detect", methods=['POST'])
def detect():
    error_response = validate_request()
    if error_response:
        return error_response, 400

    file = request.files['photo']
    ref_length_cm = float(request.form['refLength'])

    image = decode_image(file)
    pose_landmark_list = detect_pose_landmarks(image)
    if len(pose_landmark_list) == 0:
        return ResponseBuilder.failed('Nothing detected').json, 404

    pose_landmark_list = [
        set_topmost_point(adjust_shoulder(pose_landmark)) for pose_landmark in pose_landmark_list
    ]
    vec_length = get_connection_length(pose_landmark_list[0])

    ref_contour = detect_ref_obj(image)
    if ref_contour is None:
        return ResponseBuilder.failed('Ref object not detected').json, 404
    ref_length = get_contour_length(ref_contour, image.shape)
    real_height = ref_length_cm * vec_length / ref_length

    annotation_image = get_annotation(image, pose_landmark_list)
    resized_annotation = resize_image(annotation_image)
    encoded_annotation = encode_image(resized_annotation)

    data = {
        'height': real_height,
        'annotation': encoded_annotation,
    }
    return ResponseBuilder.success(data).json, 200


def main():
    # app.run(port=int(os.environ.get('PORT', 3000)))
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run()


if __name__ == "__main__":
    main()
