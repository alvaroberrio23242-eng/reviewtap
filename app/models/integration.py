from datetime import datetime, timezone

from app.extensions import db


class Integration(db.Model):
    __tablename__ = "integrations"

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(
        db.Integer, db.ForeignKey("businesses.id"), nullable=False, index=True
    )
    channel = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    label = db.Column(db.String(255))
    icon = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Integration {self.channel}>"
