from flask import Blueprint, request

from utils.response import ResponseBuilder


blueprint = Blueprint('error_handlers', __name__)


@blueprint.app_errorhandler(404)
def handle404():
    return ResponseBuilder.failed(f'Implementation not found').json


@blueprint.app_errorhandler(405)
def handle404():
    method = request.method
    return ResponseBuilder.failed(f'Method `{method}` not allowed').json


@blueprint.app_errorhandler(413)
def handle404():
    return ResponseBuilder.failed(f'Image size too large (max 2MB)').json
