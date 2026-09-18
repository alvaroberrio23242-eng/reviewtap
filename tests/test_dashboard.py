from app.models.analytics import AnalyticsEvent
from app.models.device import NFCDevice
from app.models.qrcode import QRCode
from app.extensions import db as _db


# --- Dashboard: Authentication ---

def test_dashboard_requires_auth(client, two_devices):
    response = client.get("/dashboard")
    assert response.status_code in (401, 302)


def test_dashboard_accessible_when_authenticated(client, sample_user, two_businesses):
    client.post("/login", data={"email": "test@example.com", "password": "password123"})
    response = client.get("/dashboard")
    assert response.status_code == 200


# --- Dashboard: Business Owner sees own businesses ---

def test_dashboard_shows_own_businesses(client, sample_user, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", data={"email": "test@example.com", "password": "password123"})
    response = client.get("/dashboard")
    html = response.data.decode()
    assert "Business A" in html
    assert "Business B" not in html


def test_dashboard_metrics(client, sample_user, two_businesses, two_locations, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.post("/login", data={"email": "test@example.com", "password": "password123"})
    response = client.get("/dashboard")
    html = response.data.decode()
    assert "1" in html  # 1 business for this user


def test_dashboard_no_event_fabrication(client, sample_user, two_businesses):
    client.post("/login", data={"email": "test@example.com", "password": "password123"})
    before = AnalyticsEvent.query.count()
    client.get("/dashboard")
    after = AnalyticsEvent.query.count()
    assert before == after


# --- Dashboard: Admin ---

def test_admin_can_access_dashboard(client, admin_user, two_businesses):
    client.post("/login", data={"email": "admin@example.com", "password": "admin123"})
    response = client.get("/dashboard")
    assert response.status_code == 200
    html = response.data.decode()
    assert "Business A" in html
    assert "Business B" in html


# --- Business Detail ---

def test_business_detail_requires_auth(client, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    response = client.get(f"/dashboard/business/{biz_a.id}")
    assert response.status_code in (401, 302)


def test_business_detail_owner_can_access(client, sample_user, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", data={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/dashboard/business/{biz_a.id}")
    assert response.status_code == 200
    html = response.data.decode()
    assert "Business A" in html


def test_business_detail_other_tenant_returns_404(client, sample_user, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", data={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/dashboard/business/{biz_b.id}")
    assert response.status_code == 404


def test_business_detail_admin_can_access(client, admin_user, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", data={"email": "admin@example.com", "password": "admin123"})
    response = client.get(f"/dashboard/business/{biz_a.id}")
    assert response.status_code == 200


def test_business_detail_nonexistent_returns_404(client, sample_user, two_businesses):
    client.post("/login", data={"email": "test@example.com", "password": "password123"})
    response = client.get("/dashboard/business/99999")
    assert response.status_code == 404


def test_business_detail_shows_devices(client, sample_user, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.post("/login", data={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/dashboard/business/{biz_a.id}")
    html = response.data.decode()
    assert "Device A1" in html


def test_business_detail_shows_locations(client, sample_user, two_locations):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    client.post("/login", data={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/dashboard/business/{biz_a.id}")
    html = response.data.decode()
    assert "Location A1" in html


def test_business_detail_no_reviews_fabricated(client, sample_user, two_businesses):
    client.post("/login", data={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/dashboard/business/{two_businesses[2].id}")
    html = response.data.decode()
    assert "confirmed review" not in html.lower()
    assert "reseñas recibidas" not in html.lower()
