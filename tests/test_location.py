def test_create_location(client, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.post(f"/business/{biz_a.id}/locations", json={
        "name": "New Location",
        "city": "Madrid",
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "New Location"
    assert data["city"] == "Madrid"
    assert data["business_id"] == biz_a.id


def test_create_location_empty_name(client, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.post(f"/business/{biz_a.id}/locations", json={"name": ""})
    assert response.status_code == 400


def test_create_location_other_business_returns_404(client, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.post(f"/business/{biz_b.id}/locations", json={"name": "Hacked Location"})
    assert response.status_code == 404


def test_list_locations(client, two_locations):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/business/{biz_a.id}/locations")
    assert response.status_code == 200
    data = response.get_json()
    loc_ids = [l["id"] for l in data["locations"]]
    assert loc_a1.id in loc_ids
    assert loc_b1.id not in loc_ids


def test_list_locations_other_business_returns_404(client, two_locations):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/business/{biz_b.id}/locations")
    assert response.status_code == 404


def test_get_location(client, two_locations):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/business/{biz_a.id}/locations/{loc_a1.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Location A1"


def test_get_location_other_business_returns_404(client, two_locations):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/business/{biz_a.id}/locations/{loc_b1.id}")
    assert response.status_code == 404


def test_update_location(client, two_locations):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.put(f"/business/{biz_a.id}/locations/{loc_a1.id}", json={"name": "Updated A1"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Updated A1"


def test_update_location_other_business_returns_404(client, two_locations):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.put(f"/business/{biz_a.id}/locations/{loc_b1.id}", json={"name": "Hacked"})
    assert response.status_code == 404


def test_delete_location(client, two_locations):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.delete(f"/business/{biz_a.id}/locations/{loc_a1.id}")
    assert response.status_code == 200

    response = client.get(f"/business/{biz_a.id}/locations/{loc_a1.id}")
    assert response.status_code == 404


def test_delete_location_other_business_returns_404(client, two_locations):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.delete(f"/business/{biz_a.id}/locations/{loc_b1.id}")
    assert response.status_code == 404


def test_admin_can_access_locations(client, two_locations, admin_user):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    client.post("/login", json={"email": "admin@example.com", "password": "admin123"})
    response = client.get(f"/business/{biz_a.id}/locations")
    assert response.status_code == 200
    response = client.get(f"/business/{biz_b.id}/locations")
    assert response.status_code == 200


def test_admin_can_create_location(client, two_businesses, admin_user):
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", json={"email": "admin@example.com", "password": "admin123"})
    response = client.post(f"/business/{biz_a.id}/locations", json={"name": "Admin Location"})
    assert response.status_code == 201


def test_unauthenticated_cannot_access_locations(client, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    response = client.get(f"/business/{biz_a.id}/locations")
    assert response.status_code in (401, 302)


def test_location_audit_log(client, two_businesses):
    from app.models.audit import AuditLog
    user_a, user_b, biz_a, biz_b = two_businesses
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    client.post(f"/business/{biz_a.id}/locations", json={"name": "Audit Location"})
    logs = AuditLog.query.filter_by(action="location_create").all()
    assert len(logs) >= 1
