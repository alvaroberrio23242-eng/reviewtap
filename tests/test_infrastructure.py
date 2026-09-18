from app import create_app


def test_create_app():
    app = create_app("testing")
    assert app is not None
    assert app.config["TESTING"] is True


def test_app_has_secret_key():
    app = create_app("testing")
    assert app.config["SECRET_KEY"] is not None


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "reviewtap"


def test_api_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"


def test_models_import():
    from app.models import (
        User,
        Business,
        Location,
        NFCDevice,
        QRCode,
        Campaign,
        AnalyticsEvent,
        Integration,
        Subscription,
        AuditLog,
    )

    assert User is not None
    assert Business is not None
    assert Location is not None
    assert NFCDevice is not None
    assert QRCode is not None
    assert Campaign is not None
    assert AnalyticsEvent is not None
    assert Integration is not None
    assert Subscription is not None
    assert AuditLog is not None


def test_models_create_tables(db):
    from app.models import (
        User,
        Business,
        Location,
        NFCDevice,
        QRCode,
        Campaign,
        AnalyticsEvent,
        Integration,
        Subscription,
        AuditLog,
    )

    assert User.query.count() == 0
    assert Business.query.count() == 0
    assert Location.query.count() == 0
    assert NFCDevice.query.count() == 0
    assert QRCode.query.count() == 0
    assert Campaign.query.count() == 0
    assert AnalyticsEvent.query.count() == 0
    assert Integration.query.count() == 0
    assert Subscription.query.count() == 0
    assert AuditLog.query.count() == 0


def test_user_password_hashing(db):
    from app.models import User

    user = User(email="test@example.com", full_name="Test User")
    user.set_password("secret123")
    db.session.add(user)
    db.session.commit()

    assert user.check_password("secret123") is True
    assert user.check_password("wrongpassword") is False
    assert user.password_hash != "secret123"
