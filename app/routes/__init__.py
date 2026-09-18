from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.business import business_bp
from app.routes.devices import devices_bp
from app.routes.public import public_bp
from app.routes.analytics import analytics_bp
from app.routes.api import api_bp

__all__ = [
    "auth_bp",
    "dashboard_bp",
    "business_bp",
    "devices_bp",
    "public_bp",
    "analytics_bp",
    "api_bp",
]
