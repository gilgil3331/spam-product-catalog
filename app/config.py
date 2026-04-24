import os
from dotenv import load_dotenv

load_dotenv()  # no-op on Render; loads .env locally


def _require(name):
    """Fail fast if a required secret is missing. (CONF-1)"""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' is not set. "
            "See .env.example for the full list."
        )
    return value


_env = os.environ.get("FLASK_ENV", "production")


class Config:
    # Secrets — all sourced from environment, never hardcoded (CONF-1)
    SECRET_KEY = _require("SECRET_KEY")
    DATABASE_URL = _require("DATABASE_URL")
    RECAPTCHA_SECRET_KEY = _require("RECAPTCHA_SECRET_KEY")
    RECAPTCHA_SITE_KEY = _require("RECAPTCHA_SITE_KEY")

    # Debug off in production — stack traces never reach the client (ERR-1)
    DEBUG = _env == "development"
    TESTING = False

    # Session cookie security flags (Session layer, INT-1)
    SESSION_COOKIE_SECURE = _env == "production"   # HTTPS-only transmission
    SESSION_COOKIE_HTTPONLY = True                  # JS cannot read the cookie
    SESSION_COOKIE_SAMESITE = "Strict"              # blocks cross-origin submission
    PERMANENT_SESSION_LIFETIME = 3600               # 1-hour session timeout

    # CSRF protection via Flask-WTF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # Rate limiter — in-memory storage, sufficient for single-instance free tier (DOS-1)
    RATELIMIT_STORAGE_URI = "memory://"
