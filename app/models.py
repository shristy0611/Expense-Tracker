from datetime import datetime
from app import db
import json

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    merchant = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    receipt_image_path = db.Column(db.String(500), nullable=True)
    receipt_data = db.Column(db.Text, nullable=True)
    items = db.Column(db.Text, nullable=True)  # JSON list
    shop_name = db.Column(db.String(255), nullable=True)
    tax = db.Column(db.Float, nullable=True)
    payment_method = db.Column(db.String(100), nullable=True)
    receipt_number = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    phone_number = db.Column(db.String(50), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'merchant': self.merchant,
            'amount': self.amount,
            'currency': self.currency,
            'category': self.category,
            'description': self.description,
            'receipt_image_path': self.receipt_image_path,
            'receipt_data': self.receipt_data,
            'items': json.loads(self.items) if self.items else [],
            'shop_name': self.shop_name,
            'tax': self.tax,
            'payment_method': self.payment_method,
            'receipt_number': self.receipt_number,
            'address': self.address,
            'phone_number': self.phone_number,
            'note': self.note,
        }
