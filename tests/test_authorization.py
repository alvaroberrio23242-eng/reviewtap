import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User
from app.models.business import Business
from app.services.authorization import user_owns_business, get_user_business_ids


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
def two_businesses(db):
    user_a = User(email="usera@example.com", full_name="User A", role="business_owner")
    user_a.set_password("password123")
    user_b = User(email="userb@example.com", full_name="User B", role="business_owner")
    user_b.set_password("password123")
    db.session.add_all([user_a, user_b])
    db.session.flush()

    biz_a = Business(owner_id=user_a.id, name="Business A", slug="biz-a")
    biz_b = Business(owner_id=user_b.id, name="Business B", slug="biz-b")
    db.session.add_all([biz_a, biz_b])
    db.session.commit()
    return user_a, user_b, biz_a, biz_b


@pytest.fixture
def admin_user(db):
    user = User(email="admin@example.com", full_name="Admin", role="admin")
    user.set_password("admin123")
    db.session.add(user)
    db.session.commit()
    return user


def test_user_owns_own_business(app, db, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    with app.app_context():
        with app.test_request_context():
            from flask_login import LoginManager, login_user
            login_manager = LoginManager()
            login_manager.init_app(app)

            @login_manager.user_loader
            def load_user(user_id):
                return _db.session.get(User, int(user_id))

            login_manager.login_view = "auth.login"

            login_user(user_a)

            assert user_owns_business(biz_a.id) is True
            assert user_owns_business(biz_b.id) is False


def test_admin_accesses_any_business(app, db, two_businesses, admin_user):
    user_a, user_b, biz_a, biz_b = two_businesses
    with app.app_context():
        with app.test_request_context():
            from flask_login import LoginManager, login_user
            login_manager = LoginManager()
            login_manager.init_app(app)

            @login_manager.user_loader
            def load_user(user_id):
                return _db.session.get(User, int(user_id))

            login_manager.login_view = "auth.login"

            login_user(admin_user)

            assert user_owns_business(biz_a.id) is True
            assert user_owns_business(biz_b.id) is True


def test_get_user_business_ids_owner(app, db, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    with app.app_context():
        with app.test_request_context():
            from flask_login import LoginManager, login_user
            login_manager = LoginManager()
            login_manager.init_app(app)

            @login_manager.user_loader
            def load_user(user_id):
                return _db.session.get(User, int(user_id))

            login_manager.login_view = "auth.login"

            login_user(user_a)

            ids = get_user_business_ids()
            assert biz_a.id in ids
            assert biz_b.id not in ids


def test_get_user_business_ids_admin(app, db, two_businesses, admin_user):
    user_a, user_b, biz_a, biz_b = two_businesses
    with app.app_context():
        with app.test_request_context():
            from flask_login import LoginManager, login_user
            login_manager = LoginManager()
            login_manager.init_app(app)

            @login_manager.user_loader
            def load_user(user_id):
                return _db.session.get(User, int(user_id))

            login_manager.login_view = "auth.login"

            login_user(admin_user)

            ids = get_user_business_ids()
            assert biz_a.id in ids
            assert biz_b.id in ids


def test_business_b_cannot_access_business_a(client, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses

    client.post("/login", json={
        "email": "userb@example.com",
        "password": "password123",
    })

    response = client.get(f"/business/{biz_a.id}")
    assert response.status_code == 404


def test_cross_tenant_isolation(client, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses

    client.post("/login", json={
        "email": "usera@example.com",
        "password": "password123",
    })

    response = client.get(f"/business/{biz_b.id}")
    assert response.status_code == 404


def test_user_lists_only_own_businesses(client, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses

    client.post("/login", json={
        "email": "usera@example.com",
        "password": "password123",
    })

    response = client.get("/business")
    data = response.get_json()
    biz_ids = [b["id"] for b in data["businesses"]]
    assert biz_a.id in biz_ids
    assert biz_b.id not in biz_ids


def test_unauthenticated_cannot_access_business(client, db):
    response = client.get("/business/1")
    assert response.status_code in (401, 302)
