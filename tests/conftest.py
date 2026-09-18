import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User
from app.models.business import Business
from app.models.location import Location
from app.models.device import NFCDevice
from app.models.qrcode import QRCode


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


@pytest.fixture
def two_businesses(db, sample_user):
    user2 = User(email="user2@example.com", full_name="User Two", role="business_owner")
    user2.set_password("password123")
    db.session.add(user2)
    db.session.flush()

    biz_a = Business(owner_id=sample_user.id, name="Business A", slug="business-a")
    biz_b = Business(owner_id=user2.id, name="Business B", slug="business-b")
    db.session.add_all([biz_a, biz_b])
    db.session.commit()
    return sample_user, user2, biz_a, biz_b


@pytest.fixture
def two_locations(db, two_businesses):
    user_a, user_b, biz_a, biz_b = two_businesses
    loc_a1 = Location(business_id=biz_a.id, name="Location A1", city="City A")
    loc_b1 = Location(business_id=biz_b.id, name="Location B1", city="City B")
    db.session.add_all([loc_a1, loc_b1])
    db.session.commit()
    return user_a, user_b, biz_a, biz_b, loc_a1, loc_b1


@pytest.fixture
def two_devices(db, two_locations):
    user_a, user_b, biz_a, biz_b, loc_a1, loc_b1 = two_locations
    dev_a = NFCDevice(business_id=biz_a.id, location_id=loc_a1.id, device_code="DEVICEA1", name="Device A1", status="active")
    dev_b = NFCDevice(business_id=biz_b.id, location_id=loc_b1.id, device_code="DEVICEB1", name="Device B1", status="active")
    db.session.add_all([dev_a, dev_b])
    db.session.flush()

    qr_a = QRCode(device_id=dev_a.id, url=f"/r/{dev_a.device_code}")
    qr_b = QRCode(device_id=dev_b.id, url=f"/r/{dev_b.device_code}")
    db.session.add_all([qr_a, qr_b])
    db.session.commit()
    return user_a, user_b, biz_a, biz_b, loc_a1, loc_b1, dev_a, dev_b
