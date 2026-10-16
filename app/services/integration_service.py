from urllib.parse import urlparse

from flask import request
from flask_login import current_user

from app.extensions import db
from app.models.audit import AuditLog
from app.models.business import Business
from app.models.integration import Integration

ALLOWED_CHANNELS = ("google", "tripadvisor", "whatsapp", "instagram", "facebook", "website")
MAX_URL_LENGTH = 500
MAX_LABEL_LENGTH = 255


def _log_audit(action, business_id, integration_id=None, details=None):
    ip = request.remote_addr if request else None
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        business_id=business_id,
        action=action,
        entity_type="integration",
        entity_id=integration_id,
        details=details,
        ip_address=ip,
    )
    db.session.add(log)


def validate_channel_url(channel, url):
    if not isinstance(url, str):
        return None, "URL is required"
    url = url.strip()
    if not url:
        return None, "URL is required"
    if len(url) > MAX_URL_LENGTH:
        return None, "URL is too long (max 500 characters)"
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
    except ValueError:
        return None, "URL is not valid"
    if parsed.scheme != "https" or not host:
        return None, "URL must start with https://"
    if channel == "tripadvisor" and "tripadvisor" not in host.split("."):
        return None, "TripAdvisor URL must be on a tripadvisor domain"
    return url, None


def create_integration(business_id, channel, url, label=None):
    if not isinstance(channel, str) or channel.strip().lower() not in ALLOWED_CHANNELS:
        return None, "Invalid channel"
    channel = channel.strip().lower()

    clean_url, error = validate_channel_url(channel, url)
    if error:
        return None, error

    if label is not None:
        if not isinstance(label, str):
            return None, "Label must be text"
        label = label.strip() or None
        if label and len(label) > MAX_LABEL_LENGTH:
            return None, "Label is too long (max 255 characters)"

    business = db.session.get(Business, business_id)
    if business is None or business.is_deleted:
        return None, "Business not found"

    if Integration.query.filter_by(business_id=business_id, channel=channel).first():
        return None, "This channel already exists for this business"

    last = (
        db.session.query(db.func.max(Integration.sort_order))
        .filter(Integration.business_id == business_id)
        .scalar()
    )
    integration = Integration(
        business_id=business_id,
        channel=channel,
        url=clean_url,
        label=label,
        is_active=True,
        sort_order=(last + 1) if last is not None else 0,
    )
    db.session.add(integration)
    db.session.flush()

    _log_audit(
        "integration_create",
        business_id=business_id,
        integration_id=integration.id,
        details={"channel": channel},
    )
    db.session.commit()
    return integration, None


def update_integration(integration, url=None, is_active=None):
    changed = []
    if url is not None:
        clean_url, error = validate_channel_url(integration.channel, url)
        if error:
            return None, error
        integration.url = clean_url
        changed.append("url")
    if is_active is not None:
        if not isinstance(is_active, bool):
            return None, "is_active must be true or false"
        integration.is_active = is_active
        changed.append("is_active")
    if not changed:
        return None, "Nothing to update"

    db.session.flush()
    _log_audit(
        "integration_update",
        business_id=integration.business_id,
        integration_id=integration.id,
        details={"channel": integration.channel, "fields": changed},
    )
    db.session.commit()
    return integration, None


def delete_integration(integration):
    business_id = integration.business_id
    integration_id = integration.id
    channel = integration.channel
    db.session.delete(integration)
    db.session.flush()
    _log_audit(
        "integration_delete",
        business_id=business_id,
        integration_id=integration_id,
        details={"channel": channel},
    )
    db.session.commit()
    return True, None