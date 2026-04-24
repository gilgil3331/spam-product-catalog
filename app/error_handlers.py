from flask import render_template
from app.logger import get_logger

logger = get_logger(__name__)


def register_error_handlers(app):
    """Generic error responses — no server details, DB names, or stack traces exposed. (ERR-1)"""

    @app.errorhandler(400)
    def bad_request(e):
        logger.warning(f"400: {e}")
        return render_template("error.html", code=400, message="Bad request."), 400

    @app.errorhandler(403)
    def forbidden(e):
        logger.warning(f"403: {e}")
        return render_template("error.html", code=403, message="Access denied."), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="Page not found."), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return render_template("error.html", code=405, message="Method not allowed."), 405

    @app.errorhandler(429)
    def too_many_requests(e):
        logger.warning(f"429 rate limit: {e}")
        return render_template("error.html", code=429, message="Too many requests. Please wait and try again."), 429

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"500: {e}")
        return render_template("error.html", code=500, message="An unexpected error occurred."), 500

    @app.errorhandler(Exception)
    def unhandled(e):
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return render_template("error.html", code=500, message="An unexpected error occurred."), 500
