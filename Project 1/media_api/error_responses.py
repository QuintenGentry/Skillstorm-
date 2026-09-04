""" Handle the Api Errors that result from flask """

from flask import jsonify, Response

class ApiError(Exception):
    """ Custom exception that can work with Flask's errorhandler() """

    def __init__(self, code: str, status: int, detail: str | None = None):

        # Flask expects specific values for "code"
        #   ex: "not_found" "internal" "validation_failed"

        super().__init__(detail or code)
        self.code = code
        self.status = status
        self.detail = detail

# Allows jsonify output as a response
def error_response(code: str, status: int, detail: str | None = None) -> Response:
    """ Convert error details into a json object"""
    return jsonify(error=code, detail=detail), status