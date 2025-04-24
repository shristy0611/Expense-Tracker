from datetime import datetime
from app import db


class Receipt(db.Model):
    __tablename__ = 'receipts'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    merchant = db.Column(db.String(128), nullable=True)
    date = db.Column(db.Date, nullable=True)
    total = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String(256), nullable=True)  # comma-separated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'merchant': self.merchant,
            'date': self.date.isoformat() if self.date else None,
            'total': self.total,
            'notes': self.notes,
            'tags': self.tags.split(',') if self.tags else [],
            'created_at': self.created_at.isoformat(),
        }
