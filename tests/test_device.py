def test_create_device(client, two_locations):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.post(f"/business/{biz_a.id}/devices", json={
        "name": "Test Device",
        "location_id": loc_a1.id,
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Test Device"
    assert data["device_code"] is not None
    assert len(data["device_code"]) == 8
    assert data["status"] == "inactive"


def test_create_device_generates_qr(client, two_locations):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.post(f"/business/{biz_a.id}/devices", json={"name": "QR Test"})
    assert response.status_code == 201
    device_id = response.get_json()["id"]
    device_code = response.get_json()["device_code"]

    from app.models.qrcode import QRCode
    qr = QRCode.query.filter_by(device_id=device_id).first()
    assert qr is not None
    assert qr.url.startswith("http")
    assert device_code in qr.url
    assert qr.url.endswith(f"/r/{device_code}")


def test_create_device_invalid_location(client, two_locations):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.post(f"/business/{biz_a.id}/devices", json={
        "name": "Bad Location",
        "location_id": loc_b1.id,
    })
    assert response.status_code == 400


def test_create_device_other_business_returns_404(client, two_locations):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.post(f"/business/{biz_b.id}/devices", json={"name": "Hacked"})
    assert response.status_code == 404


def test_list_devices(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/business/{biz_a.id}/devices")
    assert response.status_code == 200
    data = response.get_json()
    device_codes = [d["device_code"] for d in data["devices"]]
    assert dev_a.device_code in device_codes
    assert dev_b.device_code not in device_codes


def test_get_device(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/business/{biz_a.id}/devices/{dev_a.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["device_code"] == dev_a.device_code


def test_get_device_other_business_returns_404(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/business/{biz_a.id}/devices/{dev_b.id}")
    assert response.status_code == 404


def test_update_device(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.put(f"/business/{biz_a.id}/devices/{dev_a.id}", json={"name": "Updated Device"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Updated Device"


def test_activate_device(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.post("/login", json={"email": "test@example.com", "password": "password123"})

    dev_a.status = "inactive"
    from app.extensions import db
    db.session.commit()

    response = client.post(f"/business/{biz_a.id}/devices/{dev_a.id}/activate")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "active"
    assert data["activated_at"] is not None


def test_deactivate_device(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.post(f"/business/{biz_a.id}/devices/{dev_a.id}/deactivate")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "inactive"


def test_delete_device(client, two_locations):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    client.post("/login", json={"email": "test@example.com", "password": "password123"})

    from app.models.device import NFCDevice
    from app.extensions import db
    dev = NFCDevice(business_id=biz_a.id, device_code="DELTEST1", name="To Delete")
    db.session.add(dev)
    db.session.commit()
    dev_id = dev.id

    response = client.delete(f"/business/{biz_a.id}/devices/{dev_id}")
    assert response.status_code == 200

    response = client.get(f"/business/{biz_a.id}/devices/{dev_id}")
    assert response.status_code == 404


def test_delete_device_other_business_returns_404(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.delete(f"/business/{biz_a.id}/devices/{dev_b.id}")
    assert response.status_code == 404


def test_admin_can_access_devices(client, two_devices, admin_user):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.post("/login", json={"email": "admin@example.com", "password": "admin123"})
    response = client.get(f"/business/{biz_a.id}/devices")
    assert response.status_code == 200
    response = client.get(f"/business/{biz_b.id}/devices")
    assert response.status_code == 200


def test_get_qr(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/business/{biz_a.id}/devices/{dev_a.id}/qr")
    assert response.status_code == 200
    data = response.get_json()
    assert dev_a.device_code in data["url"]
    assert data["url"].endswith(f"/r/{dev_a.device_code}")


def test_download_qr_png(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/business/{biz_a.id}/devices/{dev_a.id}/qr/download")
    assert response.status_code == 200
    assert response.content_type == "image/png"


def test_download_qr_svg(client, two_devices):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b = two_devices
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    response = client.get(f"/business/{biz_a.id}/devices/{dev_a.id}/qr/download?format=svg")
    assert response.status_code == 200
    assert response.content_type.startswith("image/svg+xml")


def test_device_audit_log(client, two_locations):
    from app.models.audit import AuditLog
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    client.post("/login", json={"email": "test@example.com", "password": "password123"})
    client.post(f"/business/{biz_a.id}/devices", json={"name": "Audit Device"})
    logs = AuditLog.query.filter_by(action="device_create").all()
    assert len(logs) >= 1
