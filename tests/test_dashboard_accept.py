from flask import Flask

from app.routes.dashboard import request_accepts_html

BROWSER = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"


def _accepts_html(accept):
    app = Flask(__name__)
    headers = {"Accept": accept} if accept else {}
    with app.test_request_context("/dashboard", headers=headers):
        return request_accepts_html()


def test_browser_gets_html():
    assert _accepts_html(BROWSER) is True


def test_explicit_json_gets_json():
    assert _accepts_html("application/json") is False


def test_wildcard_client_gets_json():
    assert _accepts_html("*/*") is False


def test_no_accept_header_gets_json():
    assert _accepts_html(None) is False
