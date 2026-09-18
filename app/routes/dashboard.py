from flask import Blueprint, jsonify, render_template
from flask_login import login_required, current_user

from app.services.dashboard_service import get_dashboard_data, get_business_detail
from app.services.authorization import login_required as auth_login_required

dashboard_bp = Blueprint("dashboard", __name__, static_folder="../static", static_url_path="/dashboard-static")


@dashboard_bp.route("/dashboard")
@login_required
def index():
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    data = get_dashboard_data(current_user)

    if not request_accepts_html():
        return jsonify({
            "businesses": [
                {"id": b.id, "name": b.name, "slug": b.slug}
                for b in data["businesses"]
            ],
            "metrics": data["metrics"],
            "recent_events": [
                {
                    "event_type": e.event_type,
                    "channel": e.channel,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
                for e in data["recent_events"]
            ],
            "event_breakdown": data["event_breakdown"],
        })

    return render_template(
        "dashboard/index.html",
        metrics=data["metrics"],
        businesses=data["businesses"],
        recent_events=data["recent_events"],
        event_breakdown=data["event_breakdown"],
    )


@dashboard_bp.route("/dashboard/business/<int:business_id>")
@login_required
def business_detail(business_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    data = get_business_detail(current_user, business_id)

    if data is None:
        return jsonify({"error": "Resource not found"}), 404

    if not request_accepts_html():
        return jsonify({
            "business": {
                "id": data["business"].id,
                "name": data["business"].name,
                "slug": data["business"].slug,
            },
            "metrics": data["metrics"],
            "locations": [
                {"id": loc.id, "name": loc.name, "city": loc.city}
                for loc in data["locations"]
            ],
            "devices": [
                {"id": d.id, "device_code": d.device_code, "name": d.name, "status": d.status}
                for d in data["devices"]
            ],
            "recent_events": [
                {
                    "event_type": e.event_type,
                    "channel": e.channel,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
                for e in data["recent_events"]
            ],
            "event_breakdown": data["event_breakdown"],
        })

    return render_template(
        "dashboard/business.html",
        business=data["business"],
        locations=data["locations"],
        devices=data["devices"],
        metrics=data["metrics"],
        recent_events=data["recent_events"],
        event_breakdown=data["event_breakdown"],
        recent_audit=data["recent_audit"],
    )


def request_accepts_html():
    from flask import request
    return request.accept_mimetypes.accept_html and not request.accept_mimetypes.accept_json
