from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__)


@api_bp.route("/api/health")
def api_health():
    return jsonify({"status": "healthy", "version": "0.1.0"})
