import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User
from app.models.audit import AuditLog


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        yield app


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_user(db):
    user = User(email="test@example.com", full_name="Test User", role="business_owner")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_user(db):
    user = User(email="admin@example.com", full_name="Admin User", role="admin")
    user.set_password("admin123")
    db.session.add(user)
    db.session.commit()
    return user


def test_register_success(client, db):
    response = client.post("/register", json={
        "email": "new@example.com",
        "password": "password123",
        "full_name": "New User",
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["user"]["email"] == "new@example.com"
    assert data["user"]["role"] == "business_owner"


def test_register_duplicate_email(client, sample_user):
    response = client.post("/register", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Duplicate User",
    })
    assert response.status_code == 400
    assert "already registered" in response.get_json()["error"]


def test_register_invalid_email(client, db):
    response = client.post("/register", json={
        "email": "not-an-email",
        "password": "password123",
        "full_name": "Invalid Email User",
    })
    assert response.status_code == 400


def test_register_short_password(client, db):
    response = client.post("/register", json={
        "email": "short@example.com",
        "password": "123",
        "full_name": "Short Password User",
    })
    assert response.status_code == 400


def test_register_stores_hash(client, db):
    client.post("/register", json={
        "email": "hash@example.com",
        "password": "password123",
        "full_name": "Hash Test",
    })
    user = User.query.filter_by(email="hash@example.com").first()
    assert user is not None
    assert user.password_hash != "password123"
    assert user.check_password("password123")


def test_login_success(client, sample_user):
    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "password123",
    })
    assert response.status_code == 200


def test_login_wrong_password(client, sample_user):
    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401
    assert "Invalid email or password" in response.get_json()["error"]


def test_login_nonexistent_user(client, db):
    response = client.post("/login", json={
        "email": "nonexistent@example.com",
        "password": "password123",
    })
    assert response.status_code == 401
    assert "Invalid email or password" in response.get_json()["error"]


def test_login_inactive_user(client, db):
    user = User(email="inactive@example.com", full_name="Inactive", is_active=False)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    response = client.post("/login", json={
        "email": "inactive@example.com",
        "password": "password123",
    })
    assert response.status_code == 401


def test_logout(client, sample_user):
    client.post("/login", json={
        "email": "test@example.com",
        "password": "password123",
    })
    response = client.post("/logout")
    assert response.status_code == 200


def test_me_authenticated(client, sample_user):
    client.post("/login", json={
        "email": "test@example.com",
        "password": "password123",
    })
    response = client.get("/me")
    assert response.status_code == 200
    data = response.get_json()
    assert data["email"] == "test@example.com"


def test_me_unauthenticated(client, db):
    response = client.get("/me", headers={"Accept": "application/json"})
    assert response.status_code == 401


def test_audit_log_created_on_register(client, db):
    client.post("/register", json={
        "email": "audit@example.com",
        "password": "password123",
        "full_name": "Audit Test",
    })
    logs = AuditLog.query.filter_by(action="register").all()
    assert len(logs) >= 1


def test_login_next_safe_url(client, sample_user):
    response = client.post("/login?next=http://evil.com", json={
        "email": "test@example.com",
        "password": "password123",
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "redirect" not in data or data.get("redirect") != "http://evil.com"


def test_login_next_safe_relative(client, sample_user):
    response = client.post("/login?next=/dashboard", json={
        "email": "test@example.com",
        "password": "password123",
    })
    assert response.status_code == 200
