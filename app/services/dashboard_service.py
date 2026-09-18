from sqlalchemy import func

from app.extensions import db
from app.models.business import Business
from app.models.location import Location
from app.models.device import NFCDevice
from app.models.analytics import AnalyticsEvent
from app.models.audit import AuditLog


def get_dashboard_data(user):
    from flask_login import current_user

    if current_user.has_role("admin"):
        businesses = Business.query.filter_by(is_deleted=False).all()
    else:
        businesses = [b for b in current_user.businesses if not b.is_deleted]

    business_ids = [b.id for b in businesses]

    if not business_ids:
        return {
            "businesses": [],
            "metrics": {
                "total_businesses": 0,
                "total_locations": 0,
                "total_devices": 0,
                "active_devices": 0,
                "total_interactions": 0,
                "total_events": 0,
            },
            "recent_events": [],
            "event_breakdown": {},
        }

    total_locations = Location.query.filter(
        Location.business_id.in_(business_ids)
    ).count()

    total_devices = NFCDevice.query.filter(
        NFCDevice.business_id.in_(business_ids)
    ).count()

    active_devices = NFCDevice.query.filter(
        NFCDevice.business_id.in_(business_ids),
        NFCDevice.status == "active",
    ).count()

    interaction_result = db.session.query(
        func.sum(NFCDevice.interaction_count)
    ).filter(
        NFCDevice.business_id.in_(business_ids)
    ).scalar()
    total_interactions = interaction_result or 0

    total_events = AnalyticsEvent.query.filter(
        AnalyticsEvent.business_id.in_(business_ids)
    ).count()

    recent_events = AnalyticsEvent.query.filter(
        AnalyticsEvent.business_id.in_(business_ids)
    ).order_by(AnalyticsEvent.created_at.desc()).limit(20).all()

    breakdown_rows = db.session.query(
        AnalyticsEvent.event_type,
        func.count(AnalyticsEvent.id)
    ).filter(
        AnalyticsEvent.business_id.in_(business_ids)
    ).group_by(AnalyticsEvent.event_type).all()
    event_breakdown = {row[0]: row[1] for row in breakdown_rows}

    return {
        "businesses": businesses,
        "metrics": {
            "total_businesses": len(businesses),
            "total_locations": total_locations,
            "total_devices": total_devices,
            "active_devices": active_devices,
            "total_interactions": total_interactions,
            "total_events": total_events,
        },
        "recent_events": recent_events,
        "event_breakdown": event_breakdown,
    }


def get_business_detail(user, business_id):
    from flask_login import current_user
    from app.services.authorization import user_owns_business

    if not current_user.has_role("admin") and not user_owns_business(business_id):
        return None

    business = db.session.get(Business, business_id)
    if business is None or business.is_deleted:
        return None

    locations = Location.query.filter_by(business_id=business_id).all()
    devices = NFCDevice.query.filter_by(business_id=business_id).all()

    active_devices = [d for d in devices if d.status == "active"]
    total_interactions = sum(d.interaction_count or 0 for d in devices)

    recent_events = AnalyticsEvent.query.filter_by(
        business_id=business_id
    ).order_by(AnalyticsEvent.created_at.desc()).limit(20).all()

    breakdown_rows = db.session.query(
        AnalyticsEvent.event_type,
        func.count(AnalyticsEvent.id)
    ).filter_by(business_id=business_id).group_by(AnalyticsEvent.event_type).all()
    event_breakdown = {row[0]: row[1] for row in breakdown_rows}

    recent_audit = AuditLog.query.filter_by(
        business_id=business_id
    ).order_by(AuditLog.created_at.desc()).limit(10).all()

    return {
        "business": business,
        "locations": locations,
        "devices": devices,
        "metrics": {
            "total_locations": len(locations),
            "total_devices": len(devices),
            "active_devices": len(active_devices),
            "total_interactions": total_interactions,
            "total_events": sum(event_breakdown.values()),
        },
        "recent_events": recent_events,
        "event_breakdown": event_breakdown,
        "recent_audit": recent_audit,
    }
