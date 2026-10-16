from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models.business import Business
from app.models.integration import Integration
from app.services.authorization import login_required, user_owns_business
from app.services.integration_service import (
    create_integration,
    update_integration,
    delete_integration,
)

integration_bp = Blueprint("integration", __name__)


def _get_authorized_business_or_404(business_id):
    business = db.session.get(Business, business_id)
    if business is None or business.is_deleted:
        return None
    if not user_owns_business(business_id):
        return None
    return business


def _get_integration_for_business(business_id, integration_id):
    integration = db.session.get(Integration, integration_id)
    if integration is None or integration.business_id != business_id:
        return None
    return integration


def _serialize(integration):
    return {
        "id": integration.id,
        "business_id": integration.business_id,
        "channel": integration.channel,
        "url": integration.url,
        "label": integration.label,
        "is_active": integration.is_active,
        "sort_order": integration.sort_order,
    }


@integration_bp.route("/business/<int:business_id>/integrations", methods=["GET"])
@login_required
def list_channels(business_id):
    if _get_authorized_business_or_404(business_id) is None:
        return jsonify({"error": "Business not found"}), 404
    items = (
        Integration.query.filter_by(business_id=business_id)
        .order_by(Integration.sort_order, Integration.id)
        .all()
    )
    return jsonify({"integrations": [_serialize(i) for i in items]})


@integration_bp.route("/business/<int:business_id>/integrations", methods=["POST"])
@login_required
def add_channel(business_id):
    if _get_authorized_business_or_404(business_id) is None:
        return jsonify({"error": "Business not found"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body required"}), 400

    integration, error = create_integration(
        business_id=business_id,
        channel=data.get("channel"),
        url=data.get("url"),
        label=data.get("label"),
    )
    if error:
        return jsonify({"error": error}), 400
    return jsonify(_serialize(integration)), 201


@integration_bp.route(
    "/business/<int:business_id>/integrations/<int:integration_id>",
    methods=["PUT", "PATCH"],
)
@login_required
def edit_channel(business_id, integration_id):
    if _get_authorized_business_or_404(business_id) is None:
        return jsonify({"error": "Business not found"}), 404
    integration = _get_integration_for_business(business_id, integration_id)
    if integration is None:
        return jsonify({"error": "Channel not found"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body required"}), 400

    updated, error = update_integration(
        integration, url=data.get("url"), is_active=data.get("is_active")
    )
    if error:
        return jsonify({"error": error}), 400
    return jsonify(_serialize(updated))


@integration_bp.route(
    "/business/<int:business_id>/integrations/<int:integration_id>",
    methods=["DELETE"],
)
@login_required
def remove_channel(business_id, integration_id):
    if _get_authorized_business_or_404(business_id) is None:
        return jsonify({"error": "Business not found"}), 404
    integration = _get_integration_for_business(business_id, integration_id)
    if integration is None:
        return jsonify({"error": "Channel not found"}), 404

    delete_integration(integration)
    return jsonify({"message": "Channel deleted successfully"}), 200