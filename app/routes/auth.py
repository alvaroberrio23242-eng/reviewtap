from flask import Blueprint, jsonify, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user

from app.services.auth_service import register_user, authenticate_user, perform_logout
from app.services.authorization import login_required as auth_login_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/health")
def health_check():
    return jsonify({"status": "healthy", "service": "reviewtap"})


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return jsonify({"message": "Register page"}), 200

    data = request.get_json() if request.is_json else request.form

    email = data.get("email", "")
    password = data.get("password", "")
    full_name = data.get("full_name", "")

    user, error = register_user(email, password, full_name)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        }
    }), 201


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return jsonify({"message": "Login page"}), 200

    data = request.get_json() if request.is_json else request.form

    email = data.get("email", "")
    password = data.get("password", "")

    user, error = authenticate_user(email, password)

    if error:
        return jsonify({"error": error}), 401

    next_url = request.args.get("next")
    if next_url and _is_safe_url(next_url):
        return jsonify({"message": "Login successful", "redirect": next_url}), 200

    return jsonify({"message": "Login successful"}), 200


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    perform_logout()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify({
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }), 200


def _is_safe_url(target):
    from urllib.parse import urlparse, urljoin
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc
