from flask import Blueprint, jsonify, request, current_app
import json  # needed for serializing item lists
from app import db
from app.models import Transaction

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'Expense Tracker API'}), 200

@main_bp.route('/transactions', methods=['GET'])
def list_transactions():
    """List all transactions."""
    txs = Transaction.query.all()
    return jsonify([t.to_dict() for t in txs]), 200

@main_bp.route('/transactions', methods=['POST'])
def create_transaction():
    """Create a new transaction."""
    data = request.get_json() or {}
    tx = Transaction(
        merchant=data['merchant'],
        amount=data['amount'],
        currency=data.get('currency', current_app.config.get('DEFAULT_CURRENCY', 'USD')),
        category=data['category'],
        description=data.get('description'),
        receipt_data=data.get('receipt_data'),
        items=json.dumps(data.get('items', [])),
        shop_name=data.get('shop_name'),
        tax=data.get('tax'),
        payment_method=data.get('payment_method'),
        receipt_number=data.get('receipt_number'),
        address=data.get('address'),
        phone_number=data.get('phone_number'),
        note=data.get('note')
    )
    db.session.add(tx)
    db.session.commit()
    return jsonify(tx.to_dict()), 201
