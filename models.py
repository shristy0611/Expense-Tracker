from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

# Define list of supported currencies
SUPPORTED_CURRENCIES = ["USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "CNY", "INR"]

# Define categories
TRANSACTION_CATEGORIES = [
    "Food & Dining", 
    "Shopping", 
    "Entertainment", 
    "Transportation", 
    "Utilities", 
    "Housing", 
    "Healthcare", 
    "Personal Care", 
    "Education", 
    "Travel", 
    "Business Expenses", 
    "Other"
]

class Transaction(db.Model):
    """Transaction model for storing financial transactions"""
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
