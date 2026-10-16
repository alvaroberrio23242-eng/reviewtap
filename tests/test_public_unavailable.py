from app.extensions import db as _db
from app.models.analytics import AnalyticsEvent
from app.models.device import NFCDevice
from app.models.integration import Integration

BROWSER = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"


def _inactive_device(biz, code="INACTV2"):
    dev = NFCDevice(business_id=biz.id, device_code=code, name="Inactive", status="inactive")
    _db.session.add(dev)
    _db.session.commit()
    return dev


def _assert_html_404(response):
    assert response.status_code == 404
    assert "text/html" in response.content_type
    assert b"Este enlace" in response.data


def test_unavailable_html_for_inactive_device(client, two_locations):
    _, _, biz_a, _, _, _ = two_locations
    dev = _inactive_device(biz_a)
    _assert_html_404(client.get(f"/r/{dev.device_code}", headers={"Accept": BROWSER}))


def test_unavailable_html_for_unknown_device(client, db):
    _assert_html_404(client.get("/r/NONEXIST", headers={"Accept": BROWSER}))


def test_unavailable_html_for_deleted_business(client, two_devices):
    _, _, biz_a, _, _, _, dev_a, _ = two_devices
    biz_a.is_deleted = True
    _db.session.commit()
    _assert_html_404(client.get(f"/r/{dev_a.device_code}", headers={"Accept": BROWSER}))


def test_unavailable_html_for_inactive_business(client, two_devices):
    _, _, biz_a, _, _, _, dev_a, _ = two_devices
    biz_a.is_active = False
    _db.session.commit()
    _assert_html_404(client.get(f"/r/{dev_a.device_code}", headers={"Accept": BROWSER}))


def test_unavailable_json_when_json_requested(client, db):
    response = client.get("/r/NONEXIST", headers={"Accept": "application/json"})
    assert response.status_code == 404
    assert response.get_json() == {"error": "Device not found"}


def test_unavailable_json_without_accept_header(client, db):
    response = client.get("/r/NONEXIST")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Device not found"}


def test_inactive_device_scan_not_recorded(client, two_locations):
    _, _, biz_a, _, _, _ = two_locations
    dev = _inactive_device(biz_a)
    dev_id = dev.id
    client.get(f"/r/{dev.device_code}", headers={"Accept": BROWSER})
    _db.session.refresh(dev)
    assert (dev.interaction_count or 0) == 0
    assert dev.last_interaction_at is None
    assert AnalyticsEvent.query.filter_by(device_id=dev_id).count() == 0


def test_deleted_business_scan_not_recorded(client, two_devices):
    _, _, biz_a, _, _, _, dev_a, _ = two_devices
    dev_id = dev_a.id
    biz_a.is_deleted = True
    _db.session.commit()
    client.get(f"/r/{dev_a.device_code}", headers={"Accept": BROWSER})
    _db.session.refresh(dev_a)
    assert (dev_a.interaction_count or 0) == 0
    assert dev_a.last_interaction_at is None
    assert AnalyticsEvent.query.filter_by(device_id=dev_id).count() == 0


def test_unknown_device_creates_no_event(client, db):
    client.get("/r/NONEXIST", headers={"Accept": BROWSER})
    assert AnalyticsEvent.query.count() == 0


def test_empty_channels_message_shown(client, two_devices):
    _, _, _, _, _, _, dev_a, _ = two_devices
    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 200
    assert b"no configur" in response.data


def test_empty_channels_message_hidden_with_channel(client, two_devices):
    _, _, biz_a, _, _, _, dev_a, _ = two_devices
    _db.session.add(Integration(business_id=biz_a.id, channel="google", url="https://g.page/r/example", is_active=True))
    _db.session.commit()
    response = client.get(f"/r/{dev_a.device_code}")
    assert response.status_code == 200
    assert b"no configur" not in response.data