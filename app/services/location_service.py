from flask import request
from flask_login import current_user

from app.extensions import db
from app.models.business import Business
from app.models.location import Location
from app.models.audit import AuditLog


def _log_audit(action, business_id=None, location_id=None, details=None):
    ip = request.remote_addr if request else None
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        business_id=business_id,
        action=action,
        entity_type="location",
        entity_id=location_id,
        details=details,
        ip_address=ip,
    )
    db.session.add(log)


def create_location(business_id, name, **kwargs):
    name = name.strip()
    if not name or len(name) > 255:
        return None, "Name is required (max 255 characters)"

    business = db.session.get(Business, business_id)
    if business is None or business.is_deleted:
        return None, "Business not found"

    location = Location(
        business_id=business_id,
        name=name,
        **{k: v for k, v in kwargs.items() if hasattr(Location, k) and k not in ("id", "business_id", "created_at", "updated_at")}
    )
    db.session.add(location)
    db.session.flush()

    _log_audit("location_create", business_id=business_id, location_id=location.id, details={"name": name})
    db.session.commit()

    return location, None


def update_location(location, **kwargs):
    allowed_fields = {"name", "address", "city", "country", "phone", "latitude", "longitude"}
    filtered = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

    if "name" in filtered:
        new_name = filtered["name"].strip()
        if not new_name or len(new_name) > 255:
            return None, "Name is required (max 255 characters)"
        filtered["name"] = new_name

    for key, value in filtered.items():
        setattr(location, key, value)

    db.session.flush()
    _log_audit(
        "location_update",
        business_id=location.business_id,
        location_id=location.id,
        details={"fields": list(filtered.keys())},
    )
    db.session.commit()

    return location, None


def delete_location(location):
    business_id = location.business_id
    location_id = location.id
    db.session.delete(location)
    db.session.flush()
    _log_audit("location_delete", business_id=business_id, location_id=location_id)
    db.session.commit()

    return True, None
