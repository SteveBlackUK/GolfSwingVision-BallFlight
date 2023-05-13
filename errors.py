# errors.py

from flask import jsonify
from log import logger


class MissingInputError(Exception):
    def __init__(self, message="Missing required input", status_code=400):
        super().__init__(message)
        self.status_code = status_code


class InvalidInputError(Exception):
    def __init__(self, message="Invalid input", status_code=400):
        super().__init__(message)
        self.status_code = status_code


class CannotFormEllipseError(Exception):
    def __init__(self, message="Cannot form ellipse with the given points", status_code=500):
        super().__init__(message)
        self.status_code = status_code


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request_error(error):
        logger.error(f"Bad request: {error}")
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"Server error: {error}")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(MissingInputError)
    def handle_missing_input_error(error):
        response = jsonify({"error": str(error)})
        response.status_code = error.status_code
        return response

    @app.errorhandler(InvalidInputError)
    def handle_invalid_input_error(error):
        logger.error(f"Invalid Input: {error}")
        return jsonify({"error": str(error)}), error.status_code

    @app.errorhandler(CannotFormEllipseError)
    def handle_cannot_form_ellipse_error(error):
        logger.error(f"Cannot Form Ellipse: {error}")
        return jsonify({"error": str(error)}), error.status_code
