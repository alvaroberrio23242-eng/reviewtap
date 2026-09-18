from urllib.parse import urlparse

from flask import Blueprint, jsonify, render_template, request, url_for

from app.extensions import db, limiter
from app.models.analytics import AnalyticsEvent
from app.services.device_service import record_public_interaction

public_bp = Blueprint("public", __name__, static_folder="../static", static_url_path="/public-static")

ALLOWED_SCHEMES = {"https", "http"}

CHANNEL_ICONS = {
    "google": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
    "whatsapp": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>',
    "instagram": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>',
    "facebook": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>',
    "tripadvisor": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><circle cx="6.5" cy="13.5" r="4.5" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="17.5" cy="13.5" r="4.5" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="6.5" cy="13.5" r="1.5"/><circle cx="17.5" cy="13.5" r="1.5"/><path d="M12 6a8 8 0 0 1 8 2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M4 8l8 2 8-2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M4 10l8 2 8-2" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
    "website": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
}

CHANNEL_LABELS = {
    "google": "Google",
    "whatsapp": "WhatsApp",
    "instagram": "Instagram",
    "facebook": "Facebook",
    "tripadvisor": "TripAdvisor",
    "website": "Sitio web",
}


def _is_safe_url(url):
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme in ALLOWED_SCHEMES and bool(parsed.netloc)
    except Exception:
        return False


def _build_channels(business):
    channels = []
    for integ in business.integrations:
        if not integ.is_active:
            continue
        url = integ.url
        if not _is_safe_url(url):
            continue
        channel = integ.channel.lower()
        channels.append({
            "channel": channel,
            "url": url,
            "label": CHANNEL_LABELS.get(channel, integ.label or channel.title()),
            "icon_svg": CHANNEL_ICONS.get(channel, CHANNEL_ICONS["website"]),
        })
    return channels


@public_bp.route("/r/<device_code>")
@limiter.limit("60/minute")
def public_profile(device_code):
    device = record_public_interaction(
        device_code=device_code,
        ip_address=request.remote_addr,
        user_agent=str(request.user_agent),
    )

    if device is None:
        return jsonify({"error": "Device not found"}), 404

    if device.status != "active":
        return jsonify({"error": "Device is inactive"}), 404

    business = device.business

    if business.is_deleted or not business.is_active:
        return jsonify({"error": "Business not available"}), 404

    location = device.location if device.location_id else None
    channels = _build_channels(business)

    return render_template(
        "public/profile.html",
        business=business,
        location=location,
        channels=channels,
    )


@public_bp.route("/track", methods=["POST"])
@limiter.limit("30/minute")
def track_channel_click():
    channel = request.form.get("channel", "").strip()
    device_code = request.args.get("dc", "").strip()

    if not channel or channel not in CHANNEL_LABELS:
        return jsonify({"error": "Invalid channel"}), 400

    device = None
    if device_code:
        from app.models.device import NFCDevice
        device = NFCDevice.query.filter_by(device_code=device_code).first()

    event = AnalyticsEvent(
        business_id=device.business_id if device else None,
        device_id=device.id if device else None,
        location_id=device.location_id if device else None,
        event_type=f"{channel}_click",
        channel=channel,
        ip_address=request.remote_addr,
        user_agent=str(request.user_agent),
    )
    db.session.add(event)
    db.session.commit()

    return jsonify({"status": "ok"}), 201
