from flask import Blueprint, jsonify, render_template

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(401)
def unauthorized(e):
    return jsonify({"error": "Authentication required"}), 401


@errors_bp.app_errorhandler(403)
def forbidden(e):
    return jsonify({"error": "Insufficient permissions"}), 403


@errors_bp.app_errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404


@errors_bp.app_errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500
