from app.models.analytics import AnalyticsEvent

BROWSER = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
LOGIN = {"email": "test@example.com", "password": "password123"}


def _login(client):
    client.post("/login", data=LOGIN)


def _page(client, biz_id):
    response = client.get(f"/dashboard/business/{biz_id}", headers={"Accept": BROWSER})
    assert response.status_code == 200
    return response.get_data(as_text=True)


def test_page_has_delete_controls(client, two_devices):
    _, _, biz_a, _, _, _, _, _ = two_devices
    _login(client)
    html = _page(client, biz_a.id)
    assert 'id="del-dialog"' in html
    assert "data-open-del-biz" in html
    assert "data-delete-dev" in html
    assert "data-delete-loc" in html


def test_delete_device_removes_it(client, two_devices):
    _, _, biz_a, _, _, _, dev_a, _ = two_devices
    _login(client)
    response = client.delete(f"/business/{biz_a.id}/devices/{dev_a.id}")
    assert response.status_code == 200
    assert client.get(f"/business/{biz_a.id}/devices").get_json()["devices"] == []
    assert client.get(f"/business/{biz_a.id}/devices/{dev_a.id}/qr").status_code == 404


def test_delete_location_removes_its_devices(client, two_devices):
    _, _, biz_a, _, loc_a1, _, _, _ = two_devices
    _login(client)
    response = client.delete(f"/business/{biz_a.id}/locations/{loc_a1.id}")
    assert response.status_code == 200
    assert client.get(f"/business/{biz_a.id}/locations").get_json()["locations"] == []
    assert client.get(f"/business/{biz_a.id}/devices").get_json()["devices"] == []


def test_delete_location_keeps_events_with_null_location(client, db, two_devices):
    _, _, biz_a, _, loc_a1, _, dev_a, _ = two_devices
    event = AnalyticsEvent(business_id=biz_a.id, device_id=dev_a.id, location_id=loc_a1.id, event_type="device_scan")
    db.session.add(event)
    db.session.commit()
    event_id = event.id
    _login(client)
    response = client.delete(f"/business/{biz_a.id}/locations/{loc_a1.id}")
    assert response.status_code == 200
    db.session.expire_all()
    kept = db.session.get(AnalyticsEvent, event_id)
    assert kept is not None
    assert kept.location_id is None


def test_delete_business_hides_it(client, two_businesses):
    _, _, biz_a, _ = two_businesses
    _login(client)
    response = client.delete(f"/business/{biz_a.id}")
    assert response.status_code == 200
    assert "Business A" not in client.get("/dashboard", headers={"Accept": BROWSER}).get_data(as_text=True)
    assert client.get(f"/dashboard/business/{biz_a.id}", headers={"Accept": BROWSER}).status_code == 404


def test_cannot_delete_foreign_business(client, two_businesses):
    _, _, _, biz_b = two_businesses
    _login(client)
    assert client.delete(f"/business/{biz_b.id}").status_code in (403, 404)


def test_cannot_delete_foreign_device(client, two_devices):
    _, _, biz_a, biz_b, _, _, _, dev_b = two_devices
    _login(client)
    assert client.delete(f"/business/{biz_b.id}/devices/{dev_b.id}").status_code == 404
    assert client.delete(f"/business/{biz_a.id}/devices/{dev_b.id}").status_code == 404
