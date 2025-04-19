from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This will be imported by application.py
# Do not import db here to avoid circular imports

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

# Default currency
DEFAULT_CURRENCY = "USD"

# These model classes will be used with a SQLAlchemy db instance
# This will be provided by the application when imported
class Transaction:
    """Transaction model for storing financial transactions"""
    __tablename__ = 'transaction'
    
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

class ExchangeRate:
    """Exchange rate model for currency conversion"""
    __tablename__ = 'exchange_rate'
    
    def to_dict(self):
        """Convert exchange rate to dictionary for JSON responses"""
        return {
            "base_currency": self.base_currency,
            "target_currency": self.target_currency,
            "rate": self.rate,
            "last_updated": self.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        }
