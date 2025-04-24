import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from app.config import DevConfig, TestConfig, ProdConfig

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

    from app.routes import receipts_bp, upload_bp
    app.register_blueprint(upload_bp)
    app.register_blueprint(receipts_bp)

    # Register blueprints here

    return app
