from flask import request
from flask_login import current_user

from app.extensions import db
from app.models.business import Business
from app.models.audit import AuditLog
from app.services.authorization import generate_slug, ensure_unique_slug


def _log_audit(action, business_id=None, details=None):
    ip = request.remote_addr if request else None
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        business_id=business_id,
        action=action,
        entity_type="business",
        entity_id=business_id,
        details=details,
        ip_address=ip,
    )
    db.session.add(log)


def create_business(name, **kwargs):
    name = name.strip()
    if not name or len(name) > 255:
        return None, "Name is required (max 255 characters)"

    slug = kwargs.pop("slug", None)
    if slug:
        slug = slug.strip().lower()
    else:
        slug = generate_slug(name)
    slug = ensure_unique_slug(slug)

    business = Business(
        owner_id=current_user.id,
        name=name,
        slug=slug,
        **{k: v for k, v in kwargs.items() if hasattr(Business, k) and k not in ("id", "uuid", "owner_id", "created_at", "updated_at")}
    )
    db.session.add(business)
    db.session.flush()

    _log_audit("business_create", business_id=business.id, details={"name": name, "slug": slug})
    db.session.commit()

    return business, None


def update_business(business, **kwargs):
    allowed_fields = {"name", "description", "logo_url", "website", "phone", "email", "address", "city", "country", "timezone", "primary_color"}
    filtered = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

    if "name" in filtered:
        new_name = filtered["name"].strip()
        if not new_name or len(new_name) > 255:
            return None, "Name is required (max 255 characters)"
        filtered["name"] = new_name

        if business.name != new_name and "slug" not in filtered:
            new_slug = generate_slug(new_name)
            if new_slug != business.slug:
                filtered["slug"] = ensure_unique_slug(new_slug, exclude_id=business.id)

    for key, value in filtered.items():
        setattr(business, key, value)

    db.session.flush()
    _log_audit("business_update", business_id=business.id, details={"fields": list(filtered.keys())})
    db.session.commit()

    return business, None


def delete_business(business):
    business.is_deleted = True
    business.is_active = False
    db.session.flush()
    _log_audit("business_delete", business_id=business.id)
    db.session.commit()

    return True, None


def get_business_for_user(business_id):
    business = db.session.get(Business, business_id)
    if business is None or business.is_deleted:
        return None
    return business
