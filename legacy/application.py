from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging
from datetime import datetime
from models import SUPPORTED_CURRENCIES, DEFAULT_CURRENCY, TRANSACTION_CATEGORIES
from config import DevConfig, TestConfig, ProdConfig

# Initialize database (deferred)
db = SQLAlchemy()
migrate = Migrate()

# Define transaction models with SQLAlchemy
class Transaction(db.Model):
    """Transaction model for storing financial transactions"""
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    merchant = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="USD")  # Currency code
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    receipt_image_path = db.Column(db.String(500), nullable=True)
    receipt_data = db.Column(db.Text, nullable=True)
    items = db.Column(db.Text, nullable=True)  # JSON text of items
    shop_name = db.Column(db.String(255), nullable=True)
    tax = db.Column(db.Float, nullable=True)
    payment_method = db.Column(db.String(100), nullable=True)
    receipt_number = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    phone_number = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        """Convert transaction to dictionary for JSON responses"""
        return {
            "id": self.id,
            "date": self.date.strftime('%Y-%m-%d'),
            "merchant": self.merchant,
            "amount": self.amount,
            "currency": self.currency,
            "category": self.category,
            "description": self.description or "",
            "receipt_data": self.receipt_data,
            "items": self.items,
            "shop_name": self.shop_name,
            "tax": self.tax,
            "payment_method": self.payment_method,
            "receipt_number": self.receipt_number,
            "address": self.address,
            "phone_number": self.phone_number,
            "notes": self.notes
        }

class ExchangeRate(db.Model):
    """Exchange rate model for currency conversion"""
    __tablename__ = 'exchange_rate'
    id = db.Column(db.Integer, primary_key=True)
    base_currency = db.Column(db.String(3), nullable=False)
    target_currency = db.Column(db.String(3), nullable=False)
    rate = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert exchange rate to dictionary for JSON responses"""
        return {
            "base_currency": self.base_currency,
            "target_currency": self.target_currency,
            "rate": self.rate,
            "last_updated": self.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        }

# Create application factory
def create_app(config_class=None):
    app = Flask(__name__)
    # Dynamic config selection based on FLASK_ENV
    if config_class:
        cfg = config_class
    else:
        flask_env = os.getenv("FLASK_ENV", "development")
        if flask_env == "production":
            cfg = ProdConfig
        elif flask_env == "testing":
            cfg = TestConfig
        else:
            cfg = DevConfig
    app.config.from_object(cfg)

    # Disable template caching in development
    if app.config.get('DEBUG', False):
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        app.jinja_env.auto_reload = True
        print('[INFO] Template auto-reload ENABLED')

    # Print DB URI for debugging
    print("DB URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))

    # Configure logging: DEBUG level if in debug mode, else INFO
    if app.config.get('DEBUG', False):
        logging.basicConfig(level=logging.DEBUG)
        # Ensure Flask/Werkzeug logs at DEBUG
        logger.setLevel(logging.DEBUG)
        logging.getLogger('werkzeug').setLevel(logging.DEBUG)
        app.logger.setLevel(logging.DEBUG)
        print('[DEBUG] Logging set to DEBUG mode')
    else:
        logging.basicConfig(level=logging.INFO)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Create tables and seed exchange rates
    with app.app_context():
        db.create_all()
        print("[INFO] Database tables created (db.create_all called)")

    # Set upload folder config
    upload_folder = 'static/uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    app.config['UPLOAD_FOLDER'] = upload_folder

    # Apply ProxyFix middleware
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Register blueprints
    from routes import main_bp
    app.register_blueprint(main_bp)

    return app

logger = logging.getLogger(__name__)

# WSGI entrypoint
app = create_app()