from flask import Blueprint, jsonify

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics")
def list_analytics():
    return jsonify({"message": "Analytics - Coming soon"})
