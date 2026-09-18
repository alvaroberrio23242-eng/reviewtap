import re
import unicodedata
from functools import wraps

from flask import abort, jsonify
from flask_login import current_user

from app.extensions import db
from app.models.business import Business


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.has_role("admin"):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def business_owner_or_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)

        if current_user.has_role("admin"):
            return f(*args, **kwargs)

        business_id = kwargs.get("business_id")
        if business_id is None:
            for arg in args:
                if isinstance(arg, int):
                    business_id = arg
                    break

        if business_id is None:
            abort(400)

        business = db.session.get(Business, business_id)
        if business is None or business.is_deleted:
            abort(404)

        if business.owner_id != current_user.id:
            abort(404)

        return f(*args, **kwargs)
    return decorated_function


def get_user_business_ids():
    if current_user.has_role("admin"):
        return [b.id for b in Business.query.filter_by(is_deleted=False).all()]
    return [b.id for b in current_user.businesses if not b.is_deleted]


def user_owns_business(business_id):
    if current_user.has_role("admin"):
        business = db.session.get(Business, business_id)
        return business is not None and not business.is_deleted
    return any(
        b.id == business_id and not b.is_deleted
        for b in current_user.businesses
    )


def generate_slug(name):
    slug = unicodedata.normalize("NFKD", name)
    slug = slug.encode("ascii", "ignore").decode("ascii")
    slug = slug.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def ensure_unique_slug(slug, exclude_id=None):
    base_slug = slug
    candidate = base_slug
    counter = 1
    while True:
        query = Business.query.filter_by(slug=candidate, is_deleted=False)
        if exclude_id is not None:
            query = query.filter(Business.id != exclude_id)
        if not query.first():
            return candidate
        candidate = f"{base_slug}-{counter}"
        counter += 1
        if counter > 1000:
            abort(500)
