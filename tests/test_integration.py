from app.extensions import db as _db
from app.models.audit import AuditLog
from app.models.integration import Integration
from app.routes.public import CHANNEL_LABELS
from app.services.integration_service import ALLOWED_CHANNELS

BROWSER = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
LOGIN_A = {"email": "test@example.com", "password": "password123"}
LOGIN_B = {"email": "user2@example.com", "password": "password123"}
TA_URL = "https://www.tripadvisor.com/example"


def _login(client, creds=LOGIN_A):
    client.post("/login", data=creds)


def _add(client, biz_id, channel="tripadvisor", url=TA_URL):
    return client.post(f"/business/{biz_id}/integrations", json={"channel": channel, "url": url})


def _page(client, biz_id):
    response = client.get(f"/dashboard/business/{biz_id}", headers={"Accept": BROWSER})
    assert response.status_code == 200
    return response.get_data(as_text=True)


def test_allowed_channels_match_public_labels():
    assert set(ALLOWED_CHANNELS) == set(CHANNEL_LABELS)


def test_create_tripadvisor_channel_shows_public_button(client, two_devices):
    _, _, biz_a, _, _, _, dev_a, _ = two_devices
    _login(client)
    response = _add(client, biz_a.id)
    assert response.status_code == 201
    data = response.get_json()
    assert data["channel"] == "tripadvisor"
    assert data["url"] == TA_URL
    assert data["is_active"] is True
    public = client.get(f"/r/{dev_a.device_code}")
    assert public.status_code == 200
    assert b"TripAdvisor" in public.data
    assert TA_URL.encode() in public.data


def test_tripadvisor_rejects_other_domain(client, two_businesses):
    _, _, biz_a, _ = two_businesses
    _login(client)
    response = _add(client, biz_a.id, url="https://example.com/page")
    assert response.status_code == 400


def test_rejects_non_https_url(client, two_businesses):
    _, _, biz_a, _ = two_businesses
    _login(client)
    response = _add(client, biz_a.id, url="http://www.tripadvisor.com/example")
    assert response.status_code == 400


def test_rejects_unknown_channel(client, two_businesses):
    _, _, biz_a, _ = two_businesses
    _login(client)
    response = _add(client, biz_a.id, channel="myspace", url="https://example.com/x")
    assert response.status_code == 400


def test_rejects_duplicate_channel(client, two_businesses):
    _, _, biz_a, _ = two_businesses
    _login(client)
    assert _add(client, biz_a.id).status_code == 201
    assert _add(client, biz_a.id).status_code == 400


def test_other_owner_gets_404(client, two_businesses):
    _, _, biz_a, _ = two_businesses
    _login(client, LOGIN_B)
    assert _add(client, biz_a.id).status_code == 404
    assert client.get(f"/business/{biz_a.id}/integrations").status_code == 404


def test_unauthenticated_cannot_create(client, two_businesses):
    _, _, biz_a, _ = two_businesses
    response = _add(client, biz_a.id)
    assert response.status_code in (401, 302)
    assert _db.session.query(Integration).count() == 0


def test_toggle_and_delete_channel(client, two_devices):
    _, _, biz_a, _, _, _, dev_a, _ = two_devices
    _login(client)
    created = _add(client, biz_a.id)
    assert created.status_code == 201
    cid = created.get_json()["id"]
    assert TA_URL.encode() in client.get(f"/r/{dev_a.device_code}").data

    off = client.patch(f"/business/{biz_a.id}/integrations/{cid}", json={"is_active": False})
    assert off.status_code == 200
    assert off.get_json()["is_active"] is False
    assert TA_URL.encode() not in client.get(f"/r/{dev_a.device_code}").data

    gone = client.delete(f"/business/{biz_a.id}/integrations/{cid}")
    assert gone.status_code == 200
    listing = client.get(f"/business/{biz_a.id}/integrations")
    assert listing.get_json()["integrations"] == []


def test_cannot_touch_other_business_channel(client, two_businesses):
    _, _, biz_a, biz_b = two_businesses
    other = Integration(business_id=biz_b.id, channel="google", url="https://g.page/r/example", is_active=True)
    _db.session.add(other)
    _db.session.commit()
    other_id = other.id
    _login(client)
    assert client.delete(f"/business/{biz_a.id}/integrations/{other_id}").status_code == 404
    assert client.delete(f"/business/{biz_b.id}/integrations/{other_id}").status_code == 404
    patch = client.patch(f"/business/{biz_b.id}/integrations/{other_id}", json={"is_active": False})
    assert patch.status_code == 404


def test_create_writes_audit_row(client, two_businesses):
    _, _, biz_a, _ = two_businesses
    _login(client)
    assert _add(client, biz_a.id).status_code == 201
    assert AuditLog.query.filter_by(action="integration_create").count() == 1


def test_business_page_has_channels_section(client, two_businesses):
    _, _, biz_a, _ = two_businesses
    _login(client)
    html = _page(client, biz_a.id)
    assert "Canales" in html
    assert 'id="new-chan-dialog"' in html
    assert "data-open-new-chan" in html


def test_dialog_only_offers_missing_channels(client, two_businesses):
    _, _, biz_a, _ = two_businesses
    _login(client)
    assert _add(client, biz_a.id, channel="google", url="https://g.page/r/example").status_code == 201
    html = _page(client, biz_a.id)
    assert '<option value="google">' not in html
    assert '<option value="tripadvisor">' in html