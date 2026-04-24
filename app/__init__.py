from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

from app.config import Config
from app.db import close_db
from app.error_handlers import register_error_handlers

csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Security headers (INT-1, PROTO-1)
    # strict-dynamic: scripts loaded with a valid nonce may load further scripts —
    # required because reCAPTCHA's API dynamically injects inline <script> elements.
    # Host allowlist kept for browsers that don't support strict-dynamic (fallback).
    csp = {
        "default-src": "'self'",
        "script-src": [
            "'strict-dynamic'",
            "https://www.google.com",
            "https://www.gstatic.com",
        ],
        "frame-src": ["https://www.google.com", "https://recaptcha.google.com"],
        "style-src": "'self'",
        "img-src": ["'self'", "data:"],
        "connect-src": ["'self'", "https://www.google.com", "https://recaptcha.google.com"],
    }
    https_only = not app.config["DEBUG"]
    Talisman(
        app,
        force_https=https_only,                         # HTTPS enforced in production (INT-1, ENC-2)
        strict_transport_security=https_only,
        strict_transport_security_max_age=31536000,     # 1 year HSTS
        content_security_policy=csp,
        content_security_policy_nonce_in=["script-src"], # per-request nonce injected into script tags
        x_content_type_options=True,
        frame_options="DENY",                           # prevents clickjacking (PROTO-1)
        referrer_policy="strict-origin-when-cross-origin",
        session_cookie_secure=https_only,
        session_cookie_http_only=True,
        session_cookie_samesite="Strict",
    )

    csrf.init_app(app)      # CSRF tokens on all POST forms
    limiter.init_app(app)   # rate limiting (DOS-1)
    app.teardown_appcontext(close_db)
    register_error_handlers(app)

    @app.context_processor
    def inject_globals():
        return {
            "site_key": app.config["RECAPTCHA_SITE_KEY"],
            "recaptcha_enabled": not app.config["DEBUG"],
        }

    from app.routes.auth import auth_bp
    from app.routes.products import products_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)

    return app
