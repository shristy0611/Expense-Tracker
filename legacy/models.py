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
    "Meals & Entertainment",
    "Office Supplies",
    "Transportation",
    "Lodging",
    "Utilities",
    "Rent",
    "Insurance",
    "Professional Services",
    "Maintenance",
    "Advertising & Marketing",
    "Shipping & Freight",
    "IT & Software",
    "Healthcare",
    "Personal Care",
    "Education",
    "Travel",
    "Business Expenses",
    "Other"
]

# Default currency
DEFAULT_CURRENCY = "USD"

# Model classes have been moved to application.py
# Only constants remain in this file to avoid circular imports
