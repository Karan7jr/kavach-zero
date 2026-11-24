
from pathlib import Path

from flask import Flask, jsonify
from flask_wtf.csrf import CSRFError, generate_csrf

from app.config import Config
from app.extensions import db, migrate, csrf
from app.database import check_database_connection
import app.models


def create_app(test_config=None):

    app = Flask(
        __name__,
        static_folder=None
    )

    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY is not configured"
        )

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError(
            "DATABASE_URL is not configured"
        )

    Path(
        app.config["PRIVATE_STORAGE"]
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Health API
    @app.get("/api/health")
    def health():

        connected = check_database_connection()

        return jsonify({
            "project": app.config["APP_NAME"],
            "version": app.config["APP_VERSION"],
            "status": "running" if connected else "degraded",
            "database": "connected" if connected else "disconnected"
        }), 200 if connected else 503

    # CSRF token API
    @app.get("/api/auth/csrf")
    def csrf_token():

        return jsonify({
            "csrf_token": generate_csrf()
        }), 200

    # Security headers
    @app.after_request
    def security_headers(response):

        response.headers["X-Content-Type-Options"] = "nosniff"

        response.headers["X-Frame-Options"] = "DENY"

        response.headers["Referrer-Policy"] = "no-referrer"

        response.headers["Cache-Control"] = "no-store"

        return response

    # Error handlers
    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):

        return jsonify({
            "error": "CSRF validation failed"
        }), 400

    @app.errorhandler(404)
    def not_found(error):

        return jsonify({
            "error": "Resource not found"
        }), 404

    @app.errorhandler(413)
    def file_too_large(error):

        return jsonify({
            "error": "File exceeds maximum size"
        }), 413

    @app.errorhandler(500)
    def internal_error(error):

        return jsonify({
            "error": "Internal server error"
        }), 500

    return app
