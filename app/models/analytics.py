from datetime import datetime, timezone

from app.extensions import db


class AnalyticsEvent(db.Model):
    __tablename__ = "analytics_events"

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(
        db.Integer, db.ForeignKey("businesses.id"), nullable=False, index=True
    )
    device_id = db.Column(
        db.Integer, db.ForeignKey("nfc_devices.id"), nullable=True, index=True
    )
    location_id = db.Column(
        db.Integer, db.ForeignKey("locations.id"), nullable=True, index=True
    )
    event_type = db.Column(db.String(50), nullable=False, index=True)
    channel = db.Column(db.String(50))
    event_metadata = db.Column("metadata", db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True
    )

    def __repr__(self):
        return f"<AnalyticsEvent {self.event_type}>"
