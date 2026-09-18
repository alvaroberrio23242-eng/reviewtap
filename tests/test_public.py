from app.models.analytics import AnalyticsEvent
from app.models.integration import Integration
from app.extensions import db as _db


# --- Public Profile Rendering ---

def test_public_profile_renders_business(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 200
    assert b"Business A" in response.data
    assert b"ReviewTap" in response.data


def test_public_profile_renders_location(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 200
    assert b"Location A1" in response.data


def test_public_profile_no_auth_required(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 200


def test_public_profile_active_device(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 200
    assert b"Business A" in response.data


def test_public_profile_inactive_device(client, two_locations):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    from app.models.device import NFCDevice
    dev = NFCDevice(business_id=biz_a.id, device_code="INACTV1", name="Inactive", status="inactive")
    _db.session.add(dev)
    _db.session.commit()

    response = client.get("/r/INACTV1")
    assert response.status_code == 404


def test_public_profile_nonexistent_device(client, db):
    response = client.get("/r/NONEXIST")
    assert response.status_code == 404


def test_public_profile_deleted_business(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    biz_a.is_deleted = True
    _db.session.commit()

    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 404


def test_public_profile_missing_location(client, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    from app.models.device import NFCDevice
    from app.models.qrcode import QRCode
    dev = NFCDevice(business_id=biz_a.id, device_code="NOLOCA1", name="No Location", status="active")
    _db.session.add(dev)
    _db.session.flush()
    qr = QRCode(device_id=dev.id, url=f"/r/{dev.device_code}")
    _db.session.add(qr)
    _db.session.commit()

    response = client.get("/r/NOLOCA1")
    assert response.status_code == 200
    assert b"Business A" in response.data


def test_public_profile_missing_integration(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 200
    assert b"Google" not in response.data


# --- Channels ---

def test_google_button_when_configured(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    integ = Integration(business_id=biz_a.id, channel="google", url="https://g.page/r/example", is_active=True)
    _db.session.add(integ)
    _db.session.commit()

    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 200
    assert b"Google" in response.data
    assert b"https://g.page/r/example" in response.data


def test_whatsapp_button_when_configured(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    integ = Integration(business_id=biz_a.id, channel="whatsapp", url="https://wa.me/573001234567", is_active=True)
    _db.session.add(integ)
    _db.session.commit()

    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 200
    assert b"WhatsApp" in response.data
    assert b"https://wa.me/573001234567" in response.data


def test_instagram_button_when_configured(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    integ = Integration(business_id=biz_a.id, channel="instagram", url="https://instagram.com/example", is_active=True)
    _db.session.add(integ)
    _db.session.commit()

    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 200
    assert b"Instagram" in response.data


def test_facebook_button_when_configured(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    integ = Integration(business_id=biz_a.id, channel="facebook", url="https://facebook.com/example", is_active=True)
    _db.session.add(integ)
    _db.session.commit()

    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 200
    assert b"Facebook" in response.data


def test_tripadvisor_button_when_configured(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    integ = Integration(business_id=biz_a.id, channel="tripadvisor", url="https://tripadvisor.com/example", is_active=True)
    _db.session.add(integ)
    _db.session.commit()

    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 200
    assert b"TripAdvisor" in response.data


def test_website_button_when_configured(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    integ = Integration(business_id=biz_a.id, channel="website", url="https://example.com", is_active=True)
    _db.session.add(integ)
    _db.session.commit()

    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 200
    assert b"Sitio web" in response.data


def test_inactive_integration_not_shown(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    integ = Integration(business_id=biz_a.id, channel="google", url="https://g.page/r/example", is_active=False)
    _db.session.add(integ)
    _db.session.commit()

    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 200
    assert b"Google" not in response.data


# --- Security ---

def test_unsafe_url_scheme_not_shown(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    integ = Integration(business_id=biz_a.id, channel="website", url="javascript:alert(1)", is_active=True)
    _db.session.add(integ)
    _db.session.commit()

    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 200
    assert b"javascript" not in response.data


def test_data_url_not_shown(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    integ = Integration(business_id=biz_a.id, channel="website", url="data:text/html,<script>alert(1)</script>", is_active=True)
    _db.session.add(integ)
    _db.session.commit()

    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 200
    assert b"data:text/html" not in response.data


def test_no_internal_ids_exposed(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    response = client.get(f"/r/{dev_a.device_code}")
    html = response.data.decode()
    assert "password" not in html.lower()
    assert "secret" not in html.lower()
    assert "owner_id" not in html


def test_xss_payload_in_description_escaped(client, two_businesses, db):
    from app.models.user import User
    user_a, user_b, biz_a, biz_b = two_businesses
    biz_a.description = '<script>alert("xss")</script>'
    _db.session.commit()

    from app.models.device import NFCDevice
    from app.models.qrcode import QRCode
    dev = NFCDevice(business_id=biz_a.id, device_code="XSSPAY1", name="XSS Test", status="active")
    _db.session.add(dev)
    _db.session.flush()
    qr = QRCode(device_id=dev.id, url="/r/XSSPAY1")
    _db.session.add(qr)
    _db.session.commit()

    response = client.get("/r/XSSPAY1")
    assert response.status_code == 200
    assert b"<script>" not in response.data


# --- Analytics Events ---

def test_device_scan_event_recorded(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.get(f"/r/{dev_a.device_code}")
    event = AnalyticsEvent.query.filter_by(
        device_id=dev_a.id,
        event_type="device_scan",
    ).first()
    assert event is not None
    assert event.business_id == biz_a.id
    assert event.location_id == loc_a1.id


def test_page_view_not_duplicated(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.get(f"/r/{dev_a.device_code}")
    events = AnalyticsEvent.query.filter_by(device_id=dev_a.id).all()
    event_types = [e.event_type for e in events]
    assert event_types.count("device_scan") == 1
    assert "page_view" not in event_types


def test_device_scan_does_not_create_review(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.get(f"/r/{dev_a.device_code}")
    events = AnalyticsEvent.query.filter_by(device_id=dev_a.id).all()
    event_types = [e.event_type for e in events]
    assert "confirmed_review" not in event_types
    assert "google_review" not in event_types


def test_updates_last_interaction(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    assert dev_a.last_interaction_at is None
    client.get(f"/r/{dev_a.device_code}")
    _db.session.refresh(dev_a)
    assert dev_a.last_interaction_at is not None
    assert dev_a.interaction_count == 1


def test_increments_count(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.get(f"/r/{dev_a.device_code}")
    client.get(f"/r/{dev_a.device_code}")
    _db.session.refresh(dev_a)
    assert dev_a.interaction_count == 2


# --- Channel Click Tracking ---

def test_google_click_event(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    response = client.post(
        f"/track?dc={dev_a.device_code}",
        data={"channel": "google"},
    )
    assert response.status_code == 201
    event = AnalyticsEvent.query.filter_by(
        device_id=dev_a.id,
        event_type="google_click",
        channel="google",
    ).first()
    assert event is not None


def test_whatsapp_click_event(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    response = client.post(
        f"/track?dc={dev_a.device_code}",
        data={"channel": "whatsapp"},
    )
    assert response.status_code == 201
    event = AnalyticsEvent.query.filter_by(
        device_id=dev_a.id,
        event_type="whatsapp_click",
        channel="whatsapp",
    ).first()
    assert event is not None


def test_instagram_click_event(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    response = client.post(
        f"/track?dc={dev_a.device_code}",
        data={"channel": "instagram"},
    )
    assert response.status_code == 201
    event = AnalyticsEvent.query.filter_by(
        device_id=dev_a.id,
        event_type="instagram_click",
        channel="instagram",
    ).first()
    assert event is not None


def test_invalid_channel_click_rejected(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    response = client.post(
        f"/track?dc={dev_a.device_code}",
        data={"channel": "invalid_channel"},
    )
    assert response.status_code == 400


def test_click_does_not_create_review(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.post(
        f"/track?dc={dev_a.device_code}",
        data={"channel": "google"},
    )
    events = AnalyticsEvent.query.filter_by(device_id=dev_a.id).all()
    event_types = [e.event_type for e in events]
    assert "confirmed_review" not in event_types
    assert "google_review" not in event_types
    assert "google_click" in event_types


# --- Template / HTML ---

def test_html_contains_viewport_meta(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    response = client.get(f"/r/{dev_a.device_code}")
    assert b'<meta name="viewport"' in response.data


def test_html_contains_noindex(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    response = client.get(f"/r/{dev_a.device_code}")
    assert b'noindex' in response.data


def test_html_contains_css_link(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    response = client.get(f"/r/{dev_a.device_code}")
    assert b'public.css' in response.data


def test_html_contains_js_link(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    response = client.get(f"/r/{dev_a.device_code}")
    assert b'public.js' in response.data
