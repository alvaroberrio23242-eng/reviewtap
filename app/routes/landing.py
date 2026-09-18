from flask import Blueprint, render_template

landing_bp = Blueprint("landing", __name__, static_folder="../static", static_url_path="/landing-static")


@landing_bp.route("/")
def index():
    return render_template("landing/index.html")
