import os

from flask import Flask

from app.config import CONFIGS
from app.extensions import db, migrate, login_manager, csrf, limiter


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])

    _init_extensions(app)
    _register_blueprints(app)

    return app


def _init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    from app.models import (
        User,
        Business,
        Location,
        NFCDevice,
        QRCode,
        Campaign,
        AnalyticsEvent,
        Integration,
        Subscription,
        AuditLog,
    )


def _register_blueprints(app):
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.business import business_bp
    from app.routes.location import location_bp
    from app.routes.devices import devices_bp
    from app.routes.public import public_bp
    from app.routes.analytics import analytics_bp
    from app.routes.api import api_bp
    from app.routes.errors import errors_bp
    from app.routes.landing import landing_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(business_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(landing_bp)
