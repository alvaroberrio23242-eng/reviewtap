from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models.business import Business
from app.models.location import Location
from app.services.authorization import (
    login_required,
    user_owns_business,
    business_owner_or_admin,
)
from app.services.location_service import (
    create_location,
    update_location,
    delete_location,
)

location_bp = Blueprint("location", __name__)


def _get_authorized_business_or_404(business_id):
    business = db.session.get(Business, business_id)
    if business is None or business.is_deleted:
        return None
    if not user_owns_business(business_id):
        return None
    return business


def _get_location_for_business_or_404(business_id, location_id):
    location = db.session.get(Location, location_id)
    if location is None:
        return None
    if location.business_id != business_id:
        return None
    return location


@location_bp.route("/business/<int:business_id>/locations", methods=["GET"])
@login_required
def list_locations(business_id):
    business = _get_authorized_business_or_404(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    locations = Location.query.filter_by(business_id=business_id).all()
    return jsonify({
        "locations": [
            {
                "id": loc.id,
                "name": loc.name,
                "address": loc.address,
                "city": loc.city,
                "country": loc.country,
                "phone": loc.phone,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "is_active": loc.is_active,
                "created_at": loc.created_at.isoformat() if loc.created_at else None,
            }
            for loc in locations
        ]
    })


@location_bp.route("/business/<int:business_id>/locations", methods=["POST"])
@login_required
def create(business_id):
    business = _get_authorized_business_or_404(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400

    location, error = create_location(
        business_id=business_id,
        name=name,
        address=data.get("address"),
        city=data.get("city"),
        country=data.get("country"),
        phone=data.get("phone"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
    )

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "id": location.id,
        "name": location.name,
        "address": location.address,
        "city": location.city,
        "country": location.country,
        "phone": location.phone,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "is_active": location.is_active,
        "business_id": location.business_id,
    }), 201


@location_bp.route("/business/<int:business_id>/locations/<int:location_id>", methods=["GET"])
@login_required
def get_location(business_id, location_id):
    business = _get_authorized_business_or_404(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    location = _get_location_for_business_or_404(business_id, location_id)
    if location is None:
        return jsonify({"error": "Location not found"}), 404

    return jsonify({
        "id": location.id,
        "name": location.name,
        "address": location.address,
        "city": location.city,
        "country": location.country,
        "phone": location.phone,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "is_active": location.is_active,
        "business_id": location.business_id,
        "created_at": location.created_at.isoformat() if location.created_at else None,
        "updated_at": location.updated_at.isoformat() if location.updated_at else None,
    })


@location_bp.route("/business/<int:business_id>/locations/<int:location_id>", methods=["PUT", "PATCH"])
@login_required
def update(business_id, location_id):
    business = _get_authorized_business_or_404(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    location = _get_location_for_business_or_404(business_id, location_id)
    if location is None:
        return jsonify({"error": "Location not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    updated, error = update_location(location, **data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "id": updated.id,
        "name": updated.name,
        "address": updated.address,
        "city": updated.city,
        "country": updated.country,
        "phone": updated.phone,
        "latitude": updated.latitude,
        "longitude": updated.longitude,
        "is_active": updated.is_active,
        "business_id": updated.business_id,
    })


@location_bp.route("/business/<int:business_id>/locations/<int:location_id>", methods=["DELETE"])
@login_required
def delete(business_id, location_id):
    business = _get_authorized_business_or_404(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    location = _get_location_for_business_or_404(business_id, location_id)
    if location is None:
        return jsonify({"error": "Location not found"}), 404

    delete_location(location)
    return jsonify({"message": "Location deleted successfully"}), 200
