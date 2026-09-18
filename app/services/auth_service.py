import re

from flask import request
from flask_login import login_user, logout_user, current_user

from app.extensions import db
from app.models.user import User
from app.models.audit import AuditLog


def _log_audit(action, user_id=None, details=None):
    ip = request.remote_addr if request else None
    log = AuditLog(
        user_id=user_id or (current_user.id if current_user.is_authenticated else None),
        action=action,
        details=details,
        ip_address=ip,
    )
    db.session.add(log)


def _validate_email(email):
    if not email or not isinstance(email, str):
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def _validate_password(password):
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters"
    return True, None


def register_user(email, password, full_name):
    email = email.strip().lower()

    if not _validate_email(email):
        return None, "Invalid email format"

    valid, msg = _validate_password(password)
    if not valid:
        return None, msg

    if not full_name or not full_name.strip():
        return None, "Full name is required"

    if User.query.filter_by(email=email).first():
        _log_audit("register_duplicate", details={"email": email})
        db.session.commit()
        return None, "Email already registered"

    user = User(
        email=email,
        full_name=full_name.strip(),
        role="business_owner",
    )
    user.set_password(password)
    db.session.add(user)
    _log_audit("register", user_id=None, details={"email": email})
    db.session.commit()

    _log_audit("register", user_id=user.id)
    db.session.commit()

    return user, None


def authenticate_user(email, password):
    email = email.strip().lower()
    user = User.query.filter_by(email=email).first()

    if user is None or not user.check_password(password):
        _log_audit("login_failed", details={"email": email})
        db.session.commit()
        return None, "Invalid email or password"

    if not user.is_active:
        _log_audit("login_inactive", user_id=user.id)
        db.session.commit()
        return None, "Account is deactivated"

    login_user(user)
    _log_audit("login", user_id=user.id)
    db.session.commit()

    return user, None


def perform_logout():
    if current_user.is_authenticated:
        _log_audit("logout", user_id=current_user.id)
        db.session.commit()
    logout_user()
