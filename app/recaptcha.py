import requests
from flask import current_app
from app.logger import get_logger

logger = get_logger(__name__)

_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
_MIN_SCORE = 0.5  # below this threshold → treated as bot (BOT-1)


def verify_token(token, remote_ip=None):
    """Verify a reCAPTCHA v3 token server-side. Returns True if human. (BOT-1)"""
    if current_app.config.get("DEBUG"):
        return True  # skip reCAPTCHA in local dev

    if not token:
        logger.warning("reCAPTCHA token missing from request")
        return False
    try:
        payload = {
            "secret": current_app.config["RECAPTCHA_SECRET_KEY"],
            "response": token,
        }
        if remote_ip:
            payload["remoteip"] = remote_ip

        resp = requests.post(_VERIFY_URL, data=payload, timeout=5)
        resp.raise_for_status()
        result = resp.json()

        if not result.get("success"):
            logger.warning(f"reCAPTCHA failed: {result.get('error-codes')}")
            return False

        score = result.get("score", 0.0)
        if score < _MIN_SCORE:
            logger.warning(f"reCAPTCHA score too low: {score} from {remote_ip}")
            return False

        return True
    except Exception as e:
        logger.error(f"reCAPTCHA verification error: {e}")
        return False
