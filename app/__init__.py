from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=None):
    """Application factory."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_class or Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
