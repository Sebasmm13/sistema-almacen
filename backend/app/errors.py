from flask import jsonify
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

from .extensions import db


def error_response(error, message, status, details=None):
    payload = {"error": error, "message": message, "details": details or {}}
    return jsonify(payload), status


def register_error_handlers(app):
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(_error):
        db.session.rollback()
        return error_response(
            "conflict",
            "El registro entra en conflicto con datos existentes.",
            409,
        )

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return error_response("http_error", error.description, error.code)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Error no controlado", exc_info=error)
        return error_response(
            "internal_error",
            "Ocurrió un error interno. Revise los registros del backend.",
            500,
        )

