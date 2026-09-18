import uuid
from datetime import datetime, timezone

from app.extensions import db


class NFCDevice(db.Model):
    __tablename__ = "nfc_devices"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    device_code = db.Column(
        db.String(10), unique=True, nullable=False, index=True
    )
    business_id = db.Column(
        db.Integer, db.ForeignKey("businesses.id"), nullable=False, index=True
    )
    location_id = db.Column(
        db.Integer, db.ForeignKey("locations.id"), nullable=True, index=True
    )
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("campaigns.id"), nullable=True, index=True
    )
    name = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False, default="inactive")
    activated_at = db.Column(db.DateTime)
    last_interaction_at = db.Column(db.DateTime)
    interaction_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    qr_code = db.relationship(
        "QRCode", backref="device", uselist=False, lazy=True, cascade="all, delete-orphan"
    )
    events = db.relationship(
        "AnalyticsEvent", backref="device", lazy=True, cascade="save-update, merge"
    )

    @property
    def public_url(self):
        return f"/r/{self.device_code}"

    def __repr__(self):
        return f"<NFCDevice {self.device_code}>"
