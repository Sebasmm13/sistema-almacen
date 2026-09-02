from flask import Flask

from .config import Config
from .errors import register_error_handlers
from .extensions import cors, db, migrate


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["FRONTEND_URL"]}},
    )

    # Alembic necesita que los modelos estén importados al crear migraciones.
    from . import models  # noqa: F401
    from .api.health import bp as health_bp
    from .api.perfiles import bp as perfiles_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(perfiles_bp, url_prefix="/api/perfiles")
    register_error_handlers(app)

    return app

