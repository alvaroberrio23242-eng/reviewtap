from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)

login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


@login_manager.unauthorized_handler
def unauthorized():
    from flask import request, jsonify
    from flask_wtf.csrf import CSRFError
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({"error": "Authentication required"}), 401
    from flask import redirect, url_for
    return redirect(url_for("auth.login"))
