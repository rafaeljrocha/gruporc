from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import AppConfig
from app.database import init_db


def create_app() -> Flask:
    config = AppConfig.from_env()

    app = Flask(__name__, static_folder="../static", template_folder="../templates")
    app.config["SISRITHA_CONFIG"] = config
    app.config["SECRET_KEY"] = config.secret_key
    app.config["MAX_CONTENT_LENGTH"] = config.upload_max_mb * 1024 * 1024
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = config.cookies_seguros

    if config.proxy_fix:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    init_db(config)

    from app.routes.auth_routes import auth_bp
    from app.routes.paginas_routes import paginas_bp
    from app.routes.api.secretariado_api import secretariado_api_bp
    from app.routes.api.backup_api import backup_api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(paginas_bp)
    app.register_blueprint(secretariado_api_bp)
    app.register_blueprint(backup_api_bp)

    @app.route("/healthz")
    def healthz():
        return {"status": "ok"}, 200

    return app
