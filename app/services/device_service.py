import secrets
import string

from flask import request
from flask_login import current_user

from app.extensions import db
from app.models.device import NFCDevice
from app.models.qrcode import QRCode
from app.models.location import Location
from app.models.analytics import AnalyticsEvent
from app.models.audit import AuditLog


def _log_audit(action, business_id=None, device_id=None, details=None):
    ip = request.remote_addr if request else None
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        business_id=business_id,
        action=action,
        entity_type="device",
        entity_id=device_id,
        details=details,
        ip_address=ip,
    )
    db.session.add(log)


def generate_device_code(length=8):
    alphabet = string.ascii_uppercase + string.digits
    alphabet = alphabet.replace("O", "").replace("0", "").replace("I", "").replace("1", "")
    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(length))
        if not NFCDevice.query.filter_by(device_code=code).first():
            return code


def create_device(business_id, location_id=None, name=None, **kwargs):
    from flask import current_app
    from app.models.business import Business
    business = db.session.get(Business, business_id)
    if business is None or business.is_deleted:
        return None, "Business not found"

    if location_id is not None:
        location = db.session.get(Location, location_id)
        if location is None or location.business_id != business_id:
            return None, "Location not found or does not belong to this business"

    device_code = generate_device_code()

    device = NFCDevice(
        business_id=business_id,
        location_id=location_id,
        device_code=device_code,
        name=name or f"Device {device_code}",
        status="inactive",
        **{k: v for k, v in kwargs.items() if hasattr(NFCDevice, k) and k not in ("id", "uuid", "device_code", "business_id", "location_id", "created_at", "updated_at")}
    )
    db.session.add(device)
    db.session.flush()

    base_url = current_app.config.get("BASE_URL", "http://127.0.0.1:5000")
    public_url = f"{base_url}/r/{device_code}"
    qr = QRCode(device_id=device.id, url=public_url)
    db.session.add(qr)

    _log_audit("device_create", business_id=business_id, device_id=device.id, details={"device_code": device_code, "name": name})
    db.session.commit()

    return device, None


def update_device(device, **kwargs):
    allowed_fields = {"name", "location_id", "campaign_id"}
    filtered = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

    if "location_id" in filtered:
        location_id = filtered["location_id"]
        if location_id is not None:
            location = db.session.get(Location, location_id)
            if location is None or location.business_id != device.business_id:
                return None, "Location not found or does not belong to this business"

    for key, value in filtered.items():
        setattr(device, key, value)

    db.session.flush()
    _log_audit("device_update", business_id=device.business_id, device_id=device.id, details={"fields": list(filtered.keys())})
    db.session.commit()

    return device, None


def activate_device(device):
    from datetime import datetime, timezone
    device.status = "active"
    device.activated_at = datetime.now(timezone.utc)
    db.session.flush()
    _log_audit("device_activate", business_id=device.business_id, device_id=device.id)
    db.session.commit()
    return device


def deactivate_device(device):
    device.status = "inactive"
    db.session.flush()
    _log_audit("device_deactivate", business_id=device.business_id, device_id=device.id)
    db.session.commit()
    return device


def delete_device(device):
    business_id = device.business_id
    device_id = device.id
    device_code = device.device_code
    db.session.delete(device)
    db.session.flush()
    _log_audit("device_delete", business_id=business_id, device_id=device_id, details={"device_code": device_code})
    db.session.commit()
    return True


def record_public_interaction(device_code, ip_address=None, user_agent=None):
    from datetime import datetime, timezone

    device = NFCDevice.query.filter_by(device_code=device_code).first()
    if device is None:
        return None

    device.last_interaction_at = datetime.now(timezone.utc)
    device.interaction_count = (device.interaction_count or 0) + 1

    event = AnalyticsEvent(
        business_id=device.business_id,
        device_id=device.id,
        location_id=device.location_id,
        event_type="device_scan",
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.session.add(event)
    db.session.commit()

    return device
