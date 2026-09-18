from datetime import datetime, timezone

from app.extensions import db


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(
        db.Integer, db.ForeignKey("businesses.id"), unique=True, nullable=False
    )
    plan = db.Column(db.String(20), nullable=False, default="free")
    status = db.Column(db.String(20), nullable=False, default="active")
    max_locations = db.Column(db.Integer, default=1, nullable=False)
    max_devices = db.Column(db.Integer, default=1, nullable=False)
    max_users = db.Column(db.Integer, default=1, nullable=False)
    features = db.Column(db.JSON, default=dict)
    stripe_customer_id = db.Column(db.String(255))
    stripe_subscription_id = db.Column(db.String(255))
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
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
        return f"<Subscription {self.plan}>"
