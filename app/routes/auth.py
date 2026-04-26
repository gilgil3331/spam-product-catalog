import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.db import query
from app.recaptcha import verify_token
from app.logger import get_logger
from app import limiter

logger = get_logger(__name__)
auth_bp = Blueprint("auth", __name__)

# Pre-computed hash used when a username is not found, so the response time
# is identical to a failed password match — prevents timing-based user enumeration. (ERR-2)
_DUMMY_HASH = b"$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBpj2VjNBi3yIi"


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("15 per minute")
def login():
    if session.get("logged_in"):
        return redirect(url_for("products.add_product"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").encode("utf-8")
        token = request.form.get("g-recaptcha-response", "")

        # Bot check before any DB interaction (BOT-1)
        if not verify_token(token, request.remote_addr):
            logger.warning(f"Login blocked by reCAPTCHA — IP: {request.remote_addr}")
            flash("Verification failed. Please try again.")
            return render_template("login.html"), 400

        # Parameterized query — no string concatenation (DB-3)
        rows = query("SELECT password_hash FROM users WHERE username = %s", (username,))

        stored = rows[0]["password_hash"].encode() if rows else _DUMMY_HASH
        match = bcrypt.checkpw(password, stored)  # always runs — prevents timing attacks

        if not rows or not match:
            logger.warning(f"Failed login for '{username}' — IP: {request.remote_addr}")
            flash("Invalid credentials.")  # generic — never reveals if user exists (ERR-2)
            return render_template("login.html"), 401

        session["logged_in"] = True
        session["username"] = username
        logger.info(f"Login: '{username}' — IP: {request.remote_addr}")
        return redirect(url_for("products.add_product"))

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
