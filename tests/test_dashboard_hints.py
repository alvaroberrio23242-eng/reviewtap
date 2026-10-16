BROWSER = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
LOGIN = {"email": "test@example.com", "password": "password123"}


def _login(client):
    client.post("/login", data=LOGIN)


def test_business_page_sections_explain_actions(client, two_businesses):
    _, _, biz_a, _ = two_businesses
    _login(client)
    html = client.get(f"/dashboard/business/{biz_a.id}", headers={"Accept": BROWSER}).get_data(as_text=True)
    assert "Un dispositivo es una etiqueta NFC" in html
    assert "sedes o zonas" in html
    assert html.count("dash-section-hint") >= 3


def test_dashboard_sections_explain_actions(client, two_businesses):
    _login(client)
    html = client.get("/dashboard", headers={"Accept": BROWSER}).get_data(as_text=True)
    assert "Haz clic en un negocio" in html
    assert html.count("dash-section-hint") >= 2


def test_empty_dashboard_still_explains_sections(client, sample_user):
    _login(client)
    html = client.get("/dashboard", headers={"Accept": BROWSER}).get_data(as_text=True)
    assert "Haz clic en un negocio" in html
