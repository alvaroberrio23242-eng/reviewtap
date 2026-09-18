from datetime import datetime, timezone

from app.extensions import db


class QRCode(db.Model):
    __tablename__ = "qr_codes"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(
        db.Integer, db.ForeignKey("nfc_devices.id"), unique=True, nullable=False
    )
    url = db.Column(db.String(500), nullable=False)
    style = db.Column(db.String(50), default="default")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<QRCode device={self.device_id}>"
