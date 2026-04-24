from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.db import query, execute
from app.validators import validate_product_name, validate_price, validate_search_query
from app.recaptcha import verify_token
from app.logger import get_logger
from app import limiter

logger = get_logger(__name__)
products_bp = Blueprint("products", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@products_bp.route("/")
def index():
    return redirect(url_for("auth.login"))


@products_bp.route("/add", methods=["GET", "POST"])
@login_required
@limiter.limit("10 per minute")  # DOS-1
def add_product():
    if request.method == "POST":
        token = request.form.get("g-recaptcha-response", "")

        # Bot check (BOT-1)
        if not verify_token(token, request.remote_addr):
            logger.warning(f"Add-product blocked by reCAPTCHA — IP: {request.remote_addr}")
            flash("Verification failed. Please try again.")
            return render_template("add_product.html"), 400

        # Whitelist validation — server-side, not client-side (INP-1, INP-3)
        name_ok, name_val = validate_product_name(request.form.get("name", ""))
        price_ok, price_val = validate_price(request.form.get("price", ""))

        if not name_ok:
            flash(name_val)
            return render_template("add_product.html"), 400
        if not price_ok:
            flash(price_val)
            return render_template("add_product.html"), 400

        # Parameterized INSERT (DB-3)
        execute("INSERT INTO products (name, price) VALUES (%s, %s)", (name_val, price_val))
        logger.info(f"Product added by '{session.get('username')}': '{name_val}'")
        flash("Product added successfully.", "success")
        return redirect(url_for("products.add_product"))

    return render_template("add_product.html")


@products_bp.route("/search")
@login_required
@limiter.limit("30 per minute")  # DOS-1
def search():
    q = request.args.get("q", "").strip()
    results = []

    if q:
        ok, val = validate_search_query(q)
        if not ok:
            flash(val)
            return render_template("search.html", results=[], query=q), 400

        # Parameterized LIKE — user value passed as param, never concatenated (DB-3, INP-1)
        results = query(
            "SELECT name, price FROM products WHERE name ILIKE %s ORDER BY created_at DESC LIMIT 50",
            (f"%{val}%",),
        )
        logger.info(f"Search by '{session.get('username')}': '{val}' → {len(results)} results")

    return render_template("search.html", results=results, query=q)
