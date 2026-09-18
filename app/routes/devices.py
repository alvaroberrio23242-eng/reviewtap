import io
import base64

from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required, current_user

from app.extensions import db
from app.models.device import NFCDevice
from app.models.qrcode import QRCode
from app.services.authorization import login_required, user_owns_business, business_owner_or_admin
from app.services.device_service import (
    create_device,
    update_device,
    activate_device,
    deactivate_device,
    delete_device,
)

devices_bp = Blueprint("devices", __name__)


def _get_authorized_business_or_404(business_id):
    from app.models.business import Business
    business = db.session.get(Business, business_id)
    if business is None or business.is_deleted:
        return None
    if not user_owns_business(business_id):
        return None
    return business


def _get_device_for_business_or_404(business_id, device_id):
    device = db.session.get(NFCDevice, device_id)
    if device is None:
        return None
    if device.business_id != business_id:
        return None
    return device


@devices_bp.route("/business/<int:business_id>/devices", methods=["GET"])
@login_required
def list_devices(business_id):
    business = _get_authorized_business_or_404(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    devices = NFCDevice.query.filter_by(business_id=business_id).all()
    return jsonify({
        "devices": [
            {
                "id": d.id,
                "uuid": d.uuid,
                "device_code": d.device_code,
                "name": d.name,
                "status": d.status,
                "location_id": d.location_id,
                "interaction_count": d.interaction_count,
                "last_interaction_at": d.last_interaction_at.isoformat() if d.last_interaction_at else None,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in devices
        ]
    })


@devices_bp.route("/business/<int:business_id>/devices", methods=["POST"])
@login_required
def create(business_id):
    business = _get_authorized_business_or_404(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    device, error = create_device(
        business_id=business_id,
        location_id=data.get("location_id"),
        name=data.get("name"),
    )

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "id": device.id,
        "uuid": device.uuid,
        "device_code": device.device_code,
        "name": device.name,
        "status": device.status,
        "location_id": device.location_id,
        "public_url": device.public_url,
        "created_at": device.created_at.isoformat() if device.created_at else None,
    }), 201


@devices_bp.route("/business/<int:business_id>/devices/<int:device_id>", methods=["GET"])
@login_required
def get_device(business_id, device_id):
    business = _get_authorized_business_or_404(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    device = _get_device_for_business_or_404(business_id, device_id)
    if device is None:
        return jsonify({"error": "Device not found"}), 404

    return jsonify({
        "id": device.id,
        "uuid": device.uuid,
        "device_code": device.device_code,
        "name": device.name,
        "status": device.status,
        "business_id": device.business_id,
        "location_id": device.location_id,
        "campaign_id": device.campaign_id,
        "interaction_count": device.interaction_count,
        "last_interaction_at": device.last_interaction_at.isoformat() if device.last_interaction_at else None,
        "activated_at": device.activated_at.isoformat() if device.activated_at else None,
        "created_at": device.created_at.isoformat() if device.created_at else None,
        "updated_at": device.updated_at.isoformat() if device.updated_at else None,
    })


@devices_bp.route("/business/<int:business_id>/devices/<int:device_id>", methods=["PUT", "PATCH"])
@login_required
def update(business_id, device_id):
    business = _get_authorized_business_or_404(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    device = _get_device_for_business_or_404(business_id, device_id)
    if device is None:
        return jsonify({"error": "Device not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    updated, error = update_device(device, **data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "id": updated.id,
        "device_code": updated.device_code,
        "name": updated.name,
        "status": updated.status,
        "location_id": updated.location_id,
    })


@devices_bp.route("/business/<int:business_id>/devices/<int:device_id>/activate", methods=["POST"])
@login_required
def activate(business_id, device_id):
    business = _get_authorized_business_or_404(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    device = _get_device_for_business_or_404(business_id, device_id)
    if device is None:
        return jsonify({"error": "Device not found"}), 404

    activated = activate_device(device)
    return jsonify({
        "id": activated.id,
        "device_code": activated.device_code,
        "status": activated.status,
        "activated_at": activated.activated_at.isoformat() if activated.activated_at else None,
    })


@devices_bp.route("/business/<int:business_id>/devices/<int:device_id>/deactivate", methods=["POST"])
@login_required
def deactivate(business_id, device_id):
    business = _get_authorized_business_or_404(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    device = _get_device_for_business_or_404(business_id, device_id)
    if device is None:
        return jsonify({"error": "Device not found"}), 404

    deactivated = deactivate_device(device)
    return jsonify({
        "id": deactivated.id,
        "device_code": deactivated.device_code,
        "status": deactivated.status,
    })


@devices_bp.route("/business/<int:business_id>/devices/<int:device_id>", methods=["DELETE"])
@login_required
def delete(business_id, device_id):
    business = _get_authorized_business_or_404(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    device = _get_device_for_business_or_404(business_id, device_id)
    if device is None:
        return jsonify({"error": "Device not found"}), 404

    delete_device(device)
    return jsonify({"message": "Device deleted successfully"}), 200


@devices_bp.route("/business/<int:business_id>/devices/<int:device_id>/qr", methods=["GET"])
@login_required
def get_qr(business_id, device_id):
    business = _get_authorized_business_or_404(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    device = _get_device_for_business_or_404(business_id, device_id)
    if device is None:
        return jsonify({"error": "Device not found"}), 404

    qr = QRCode.query.filter_by(device_id=device.id).first()
    if qr is None:
        return jsonify({"error": "QR code not generated yet"}), 404

    return jsonify({
        "id": qr.id,
        "url": qr.url,
        "style": qr.style,
        "is_active": qr.is_active,
        "device_code": device.device_code,
    })


@devices_bp.route("/business/<int:business_id>/devices/<int:device_id>/qr/download", methods=["GET"])
@login_required
def download_qr(business_id, device_id):
    import qrcode
    import qrcode.image.svg

    business = _get_authorized_business_or_404(business_id)
    if business is None:
        return jsonify({"error": "Business not found"}), 404

    device = _get_device_for_business_or_404(business_id, device_id)
    if device is None:
        return jsonify({"error": "Device not found"}), 404

    qr = QRCode.query.filter_by(device_id=device.id).first()
    if qr is None:
        return jsonify({"error": "QR code not generated yet"}), 404

    format_type = request.args.get("format", "png")

    if format_type == "svg":
        factory = qrcode.image.svg.SvgPathImage
        img = qrcode.make(qr.url, image_factory=factory)
        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)
        return send_file(buf, mimetype="image/svg+xml", as_attachment=True, download_name=f"reviewtap-{device.device_code}.svg")
    else:
        img = qrcode.make(qr.url)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return send_file(buf, mimetype="image/png", as_attachment=True, download_name=f"reviewtap-{device.device_code}.png")
