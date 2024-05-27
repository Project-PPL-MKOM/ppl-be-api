from re import match as re_match
from flask import request
from magic import from_buffer
from werkzeug.datastructures import FileStorage
from utils.response import ResponseBuilder


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def is_ext_allowed(filename: str):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_mime_type_allowed(file: FileStorage):
    mime = from_buffer(file.stream.read(2048), mime=True)
    file.stream.seek(0)  # Reset file pointer after reading
    return mime in ['image/png', 'image/jpeg', 'image/jpg']


def is_number_regex(s):
    """ Returns True if string is a number. """
    if re_match("^\d+?\.\d+?$", s) is None:
        return s.isdigit()
    return True


def validate_request():
    if 'photo' not in request.files:
        return ResponseBuilder.failed('Missing `photo`').json
    image = request.files['photo']
    if image.filename == '':
        return ResponseBuilder.failed('Image name can`t be empty').json
    if not is_ext_allowed(image.filename) or not is_mime_type_allowed(image):
        return ResponseBuilder.failed('Image extension must be .png, .jpg, or .jpeg').json

    if 'refLength' not in request.form:
        return ResponseBuilder.failed('Missing `refLength`').json
    refLength = request.form['refLength']
    if not is_number_regex(refLength):
        return ResponseBuilder.failed('refLength must be numeric').json
    refLength = float(refLength)
    if refLength <= 0:
        return ResponseBuilder.failed('refLength must be positive number').json
