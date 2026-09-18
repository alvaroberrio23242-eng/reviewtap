from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from app.models.business import Business
from app.services.authorization import (
    login_required,
    user_owns_business,
    get_user_business_ids,
    business_owner_or_admin,
)
from app.services.business_service import (
    create_business,
    update_business,
    delete_business,
    get_business_for_user,
)

business_bp = Blueprint("business", __name__)


@business_bp.route("/business", methods=["GET"])
@login_required
def list_businesses():
    ids = get_user_business_ids()
    businesses = Business.query.filter(
        Business.id.in_(ids),
        Business.is_deleted == False,
    ).all()
    return jsonify({
        "businesses": [
            {
                "id": b.id,
                "uuid": b.uuid,
                "name": b.name,
                "slug": b.slug,
                "description": b.description,
                "is_active": b.is_active,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            }
            for b in businesses
        ]
    })


@business_bp.route("/business", methods=["POST"])
@login_required
def create():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400

    business, error = create_business(
        name=name,
        slug=data.get("slug"),
        description=data.get("description"),
        website=data.get("website"),
        phone=data.get("phone"),
        email=data.get("email"),
        address=data.get("address"),
        city=data.get("city"),
        country=data.get("country"),
    )

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "id": business.id,
        "uuid": business.uuid,
        "name": business.name,
        "slug": business.slug,
        "description": business.description,
        "is_active": business.is_active,
    }), 201


@business_bp.route("/business/<int:business_id>", methods=["GET"])
@login_required
def get_business(business_id):
    business = get_business_for_user(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    if not user_owns_business(business_id):
        return jsonify({"error": "Business not found"}), 404

    return jsonify({
        "id": business.id,
        "uuid": business.uuid,
        "name": business.name,
        "slug": business.slug,
        "description": business.description,
        "logo_url": business.logo_url,
        "website": business.website,
        "phone": business.phone,
        "email": business.email,
        "address": business.address,
        "city": business.city,
        "country": business.country,
        "timezone": business.timezone,
        "primary_color": business.primary_color,
        "is_active": business.is_active,
        "owner_id": business.owner_id,
        "created_at": business.created_at.isoformat() if business.created_at else None,
        "updated_at": business.updated_at.isoformat() if business.updated_at else None,
    })


@business_bp.route("/business/<int:business_id>", methods=["PUT", "PATCH"])
@business_owner_or_admin
def update(business_id):
    business = get_business_for_user(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    updated, error = update_business(business, **data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "id": updated.id,
        "uuid": updated.uuid,
        "name": updated.name,
        "slug": updated.slug,
        "description": updated.description,
        "is_active": updated.is_active,
    })


@business_bp.route("/business/<int:business_id>", methods=["DELETE"])
@business_owner_or_admin
def delete(business_id):
    business = get_business_for_user(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    delete_business(business)
    return jsonify({"message": "Business deleted successfully"}), 200
