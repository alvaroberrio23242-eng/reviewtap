BROWSER = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
LOGIN = {"email": "test@example.com", "password": "password123"}


def _login(client):
    client.post("/login", data=LOGIN)


def _page(client, biz_id):
    response = client.get(f"/dashboard/business/{biz_id}", headers={"Accept": BROWSER})
    assert response.status_code == 200
    return response.get_data(as_text=True)


def test_business_page_has_create_dialogs(client, two_businesses):
    _, _, biz_a, _ = two_businesses
    _login(client)
    html = _page(client, biz_a.id)
    assert 'id="new-loc-dialog"' in html
    assert 'id="new-dev-dialog"' in html
    assert "data-open-new-loc" in html
    assert "data-open-new-dev" in html


def test_created_location_is_listed(client, two_businesses):
    _, _, biz_a, _ = two_businesses
    _login(client)
    response = client.post(f"/business/{biz_a.id}/locations", json={"name": "Sede Centro", "city": "Medellin"})
    assert response.status_code == 201
    assert "Sede Centro" in _page(client, biz_a.id)


def test_created_device_is_listed_with_qr_link(client, two_locations):
    _, _, biz_a, _, loc_a1, _ = two_locations
    _login(client)
    response = client.post(f"/business/{biz_a.id}/devices", json={"name": "Mesa 1", "location_id": loc_a1.id})
    assert response.status_code == 201
    data = response.get_json()
    html = _page(client, biz_a.id)
    assert "Mesa 1" in html
    assert data["device_code"] in html
    assert f"/business/{biz_a.id}/devices/{data['id']}/qr/download" in html


def test_device_dialog_lists_only_own_locations(client, two_locations):
    _, _, biz_a, _, _, _ = two_locations
    _login(client)
    html = _page(client, biz_a.id)
    assert "Location A1" in html
    assert "Location B1" not in html


def test_cannot_create_device_in_foreign_location(client, two_locations):
    _, _, biz_a, _, _, loc_b1 = two_locations
    _login(client)
    response = client.post(f"/business/{biz_a.id}/devices", json={"name": "Intruso", "location_id": loc_b1.id})
    assert response.status_code == 400


def test_activate_device_updates_panel_button(client, two_businesses):
    _, _, biz_a, _ = two_businesses
    _login(client)
    device_id = client.post(f"/business/{biz_a.id}/devices", json={"name": "Barra"}).get_json()["id"]
    assert "Activar" in _page(client, biz_a.id)
    response = client.post(f"/business/{biz_a.id}/devices/{device_id}/activate")
    assert response.status_code < 400
    assert "Desactivar" in _page(client, biz_a.id)
