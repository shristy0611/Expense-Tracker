import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from app.config import DevConfig, TestConfig, ProdConfig
from flasgger import Swagger

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=False)

    # Determine config
    env = config_name or os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object(ProdConfig)
    elif env == 'testing':
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(DevConfig)

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    # --- Swagger/OpenAPI integration ---
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,  # all endpoints
                "model_filter": lambda tag: True,  # all models
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }
    Swagger(app, config=swagger_config)
    # --- End Swagger/OpenAPI integration ---

    # --- Flask-Profiler integration ---
    if app.config.get("FLASK_PROFILER", {}).get("enabled"):
        from flask_profiler import Profiler
        Profiler(app)
    from app.routes import receipts_bp, upload_bp
    app.register_blueprint(upload_bp)
    app.register_blueprint(receipts_bp)

    # Register blueprints here

    return app
