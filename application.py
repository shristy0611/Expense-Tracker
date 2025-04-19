from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-dev-secret")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
db = SQLAlchemy(app)

# Import database models
from models import SUPPORTED_CURRENCIES, DEFAULT_CURRENCY
from datetime import datetime

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
            "items": self.items
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

# Create database tables
with app.app_context():
    db.create_all()
    
    # Initialize exchange rates if they don't exist
    if ExchangeRate.query.count() == 0:
        logger.info("Initializing exchange rates...")
        # Add sample rates for demonstration
        base_rates = [
            ExchangeRate(base_currency="USD", target_currency="EUR", rate=0.93),
            ExchangeRate(base_currency="USD", target_currency="JPY", rate=153.5),
            ExchangeRate(base_currency="USD", target_currency="GBP", rate=0.80),
            ExchangeRate(base_currency="USD", target_currency="AUD", rate=1.52),
            ExchangeRate(base_currency="USD", target_currency="CAD", rate=1.37),
            ExchangeRate(base_currency="USD", target_currency="CHF", rate=0.91),
            ExchangeRate(base_currency="USD", target_currency="CNY", rate=7.24),
            ExchangeRate(base_currency="USD", target_currency="INR", rate=83.45)
        ]
        
        for rate in base_rates:
            db.session.add(rate)
            
        try:
            db.session.commit()
            logger.info("Exchange rates initialized successfully")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error initializing exchange rates: {str(e)}")

# Import routes
import routes