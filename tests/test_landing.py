def test_landing_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_landing_no_auth_required(client):
    response = client.get("/")
    assert response.status_code == 200


def test_landing_contains_reviewtap(client):
    response = client.get("/")
    html = response.data.decode()
    assert "ReviewTap" in html


def test_landing_contains_cta(client):
    response = client.get("/")
    html = response.data.decode()
    assert "/register" in html
    assert "/login" in html


def test_landing_contains_nfc(client):
    response = client.get("/")
    html = response.data.decode()
    assert "NFC" in html


def test_landing_contains_qr(client):
    response = client.get("/")
    html = response.data.decode()
    assert "QR" in html


def test_landing_contains_analytics(client):
    response = client.get("/")
    html = response.data.decode()
    assert "analytics" in html.lower() or "Analytics" in html


def test_landing_contains_how_it_works(client):
    response = client.get("/")
    html = response.data.decode()
    assert "Cómo funciona" in html


def test_landing_contains_title(client):
    response = client.get("/")
    html = response.data.decode()
    assert "<title>" in html
    assert "ReviewTap" in html


def test_landing_contains_description(client):
    response = client.get("/")
    html = response.data.decode()
    assert '<meta name="description"' in html


def test_landing_no_noindex(client):
    response = client.get("/")
    html = response.data.decode()
    assert "noindex" not in html


def test_landing_contains_viewport(client):
    response = client.get("/")
    html = response.data.decode()
    assert '<meta name="viewport"' in html


def test_landing_contains_features(client):
    response = client.get("/")
    html = response.data.decode()
    assert "Características" in html or "caracteristicas" in html


def test_landing_contains_benefits(client):
    response = client.get("/")
    html = response.data.decode()
    assert "Beneficios" in html or "beneficios" in html


def test_landing_contains_footer(client):
    response = client.get("/")
    html = response.data.decode()
    assert "footer" in html.lower()
