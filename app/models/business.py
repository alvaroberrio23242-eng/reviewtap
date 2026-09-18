import uuid
from datetime import datetime, timezone

from app.extensions import db


class Business(db.Model):
    __tablename__ = "businesses"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(500))
    website = db.Column(db.String(500))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    timezone = db.Column(db.String(50), default="UTC")
    primary_color = db.Column(db.String(7), default="#2563EB")
    secondary_color = db.Column(db.String(7), default="#64748B")
    cover_image_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    locations = db.relationship(
        "Location", backref="business", lazy=True, cascade="all, delete-orphan"
    )
    devices = db.relationship(
        "NFCDevice", backref="business", lazy=True, cascade="all, delete-orphan"
    )
    campaigns = db.relationship(
        "Campaign", backref="business", lazy=True, cascade="all, delete-orphan"
    )
    integrations = db.relationship(
        "Integration", backref="business", lazy=True, cascade="all, delete-orphan"
    )
    subscription = db.relationship(
        "Subscription", backref="business", uselist=False, lazy=True
    )

    def __repr__(self):
        return f"<Business {self.name}>"
