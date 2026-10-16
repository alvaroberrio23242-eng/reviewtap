BROWSER = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
LOGIN = {"email": "test@example.com", "password": "password123"}


def _login(client):
    client.post("/login", data=LOGIN)


def test_empty_dashboard_offers_create_button(client, sample_user):
    _login(client)
    html = client.get("/dashboard", headers={"Accept": BROWSER}).get_data(as_text=True)
    assert "Sin negocios" in html
    assert "Crear negocio" in html
    assert 'id="new-biz-dialog"' in html


def test_dashboard_with_businesses_shows_header_button(client, sample_user, two_businesses):
    _login(client)
    html = client.get("/dashboard", headers={"Accept": BROWSER}).get_data(as_text=True)
    assert "+ Nuevo negocio" in html
    assert "data-open-new-biz" in html


def test_create_business_returns_id(client, sample_user):
    _login(client)
    response = client.post("/business", json={"name": "Cafe Prueba", "city": "Medellin"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"]
    assert data["name"] == "Cafe Prueba"


def test_created_business_page_is_html(client, sample_user):
    _login(client)
    biz_id = client.post("/business", json={"name": "Bar Prueba"}).get_json()["id"]
    response = client.get(f"/dashboard/business/{biz_id}", headers={"Accept": BROWSER})
    assert response.status_code == 200
    assert "text/html" in response.content_type
