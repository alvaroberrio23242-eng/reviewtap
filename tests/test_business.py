def test_create_business(client, sample_user):
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.post("/business", json={"name": "New Business"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "New Business"
    assert data["slug"] == "new-business"
    assert data["id"] is not None


def test_create_business_custom_slug(client, sample_user):
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.post("/business", json={"name": "My Business", "slug": "custom-slug"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["slug"] == "custom-slug"


def test_create_business_empty_name(client, sample_user):
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.post("/business", json={"name": ""})
    assert response.status_code == 400


def test_create_business_no_body(client, sample_user):
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.post("/business", content_type="application/json")
    assert response.status_code == 400


def test_create_business_duplicate_slug(client, sample_user, two_businesses):
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.post("/business", json={"name": "Another Business", "slug": "business-a"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["slug"] != "business-a"


def test_list_own_businesses(client, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.get("/business")
    assert response.status_code == 200
    data = response.get_json()
    biz_ids = [b["id"] for b in data["businesses"]]
    assert biz_a.id in biz_ids
    assert biz_b.id not in biz_ids


def test_get_own_business(client, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/business/{biz_a.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Business A"


def test_get_other_business_returns_404(client, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/business/{biz_b.id}")
    assert response.status_code == 404


def test_update_own_business(client, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.put(f"/business/{biz_a.id}", json={"name": "Updated A"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Updated A"


def test_update_other_business_returns_404(client, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.put(f"/business/{biz_b.id}", json={"name": "Hacked"})
    assert response.status_code == 404


def test_delete_own_business(client, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.delete(f"/business/{biz_a.id}")
    assert response.status_code == 200

    response = client.get(f"/business/{biz_a.id}")
    assert response.status_code == 404


def test_delete_other_business_returns_404(client, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.delete(f"/business/{biz_b.id}")
    assert response.status_code == 404


def test_admin_can_access_any_business(client, two_businesses, admin_user):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", json={"email": "admin@example.com", "password": "admin123"})
    response = client.get(f"/business/{biz_a.id}")
    assert response.status_code == 200
    response = client.get(f"/business/{biz_b.id}")
    assert response.status_code == 200


def test_admin_can_update_any_business(client, two_businesses, admin_user):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", json={"email": "admin@example.com", "password": "admin123"})
    response = client.put(f"/business/{biz_a.id}", json={"name": "Admin Updated A"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Admin Updated A"


def test_unauthenticated_cannot_create_business(client, db):
    response = client.post("/business", json={"name": "Test"})
    assert response.status_code in (401, 302)


def test_business_audit_log(client, db):
    from app.models.audit import AuditLog
    client.post("/register", json={
        "email": "auditbiz@example.com",
        "password": "password123",
        "full_name": "Audit Biz",
    })
    client.post("/login", json={"email": "auditbiz@example.com", "password": "password123"})
    client.post("/business", json={"name": "Audit Business"})
    logs = AuditLog.query.filter_by(action="business_create").all()
    assert len(logs) >= 1
