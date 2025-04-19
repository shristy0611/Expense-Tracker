import os
import logging
import json
import base64
import io
import time
import requests
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
import google.generativeai as genai
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-dev-secret")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Import models
from models import db, Transaction, ExchangeRate, TRANSACTION_CATEGORIES, SUPPORTED_CURRENCIES

# Initialize the database with the app
db.init_app(app)

# Configure Google Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "your-gemini-api-key"))

# Set default currency
DEFAULT_CURRENCY = "USD"

# Configure upload folder for receipts
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create all database tables
with app.app_context():
    db.create_all()
    
    # Initialize exchange rates if they don't exist
    if ExchangeRate.query.count() == 0:
        # Add sample rates for demonstration
        base_rates = [
            ExchangeRate(base_currency="USD", target_currency="EUR", rate=0.93),
            ExchangeRate(base_currency="USD", target_currency="JPY", rate=153.5),
            ExchangeRate(base_currency="USD", target_currency="GBP", rate=0.80),
            ExchangeRate(base_currency="USD", target_currency="AUD", rate=1.52),
            ExchangeRate(base_currency="USD", target_currency="CAD", rate=1.37),
            ExchangeRate(base_currency="USD", target_currency="CHF", rate=0.91),
            ExchangeRate(base_currency="USD", target_currency="CNY", rate=7.23),
            ExchangeRate(base_currency="USD", target_currency="INR", rate=83.5)
        ]
        db.session.add_all(base_rates)
        db.session.commit()

# Currency exchange rate update function
def update_exchange_rates():
    """Update exchange rates from a public API once per day"""
    try:
        # Check if rates need updating (last update was more than 24 hours ago)
        last_update = ExchangeRate.query.order_by(ExchangeRate.last_updated.desc()).first()
        
        if last_update and (datetime.utcnow() - last_update.last_updated).total_seconds() < 86400:
            logger.info("Exchange rates are up-to-date")
            return
            
        # For this demo, we'll use a free API that doesn't require authentication
        # In production, you would use a more reliable service with an API key
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            rates = data.get("rates", {})
            
            # Update exchange rates in the database
            for currency in SUPPORTED_CURRENCIES:
                if currency == "USD":  # Skip base currency
                    continue
                    
                if currency in rates:
                    # Check if rate exists
                    rate_record = ExchangeRate.query.filter_by(
                        base_currency="USD", 
                        target_currency=currency
                    ).first()
                    
                    if rate_record:
                        rate_record.rate = rates[currency]
                        rate_record.last_updated = datetime.utcnow()
                    else:
                        new_rate = ExchangeRate(
                            base_currency="USD",
                            target_currency=currency,
                            rate=rates[currency]
                        )
                        db.session.add(new_rate)
            
            db.session.commit()
            logger.info("Exchange rates updated successfully")
        else:
            logger.error(f"Failed to fetch exchange rates: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error updating exchange rates: {str(e)}")

# Convert amount between currencies
def convert_currency(amount, from_currency, to_currency):
    """Convert an amount from one currency to another using stored exchange rates"""
    if from_currency == to_currency:
        return amount
        
    try:
        # If converting from USD to another currency
        if from_currency == "USD":
            rate = ExchangeRate.query.filter_by(
                base_currency="USD", 
                target_currency=to_currency
            ).first()
            
            if rate:
                return amount * rate.rate
                
        # If converting from another currency to USD
        elif to_currency == "USD":
            rate = ExchangeRate.query.filter_by(
                base_currency="USD", 
                target_currency=from_currency
            ).first()
            
            if rate:
                return amount / rate.rate
                
        # If converting between two non-USD currencies
        else:
            # Convert to USD first, then to target currency
            from_rate = ExchangeRate.query.filter_by(
                base_currency="USD", 
                target_currency=from_currency
            ).first()
            
            to_rate = ExchangeRate.query.filter_by(
                base_currency="USD", 
                target_currency=to_currency
            ).first()
            
            if from_rate and to_rate:
                usd_amount = amount / from_rate.rate
                return usd_amount * to_rate.rate
                
        # If no conversion found, return original amount
        logger.warning(f"No exchange rate found for {from_currency} to {to_currency}")
        return amount
        
    except Exception as e:
        logger.error(f"Error converting currency: {str(e)}")
        return amount

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Try to update exchange rates when dashboard is loaded
    try:
        update_exchange_rates()
    except Exception as e:
        logger.error(f"Failed to update exchange rates on dashboard load: {str(e)}")
        
    return render_template('dashboard.html', 
                          currencies=SUPPORTED_CURRENCIES,
                          default_currency=DEFAULT_CURRENCY)

@app.route('/upload')
def upload():
    return render_template('upload.html', 
                          categories=TRANSACTION_CATEGORIES,
                          currencies=SUPPORTED_CURRENCIES,
                          default_currency=DEFAULT_CURRENCY)

@app.route('/transactions')
def transactions():
    return render_template('transactions.html', 
                          categories=TRANSACTION_CATEGORIES,
                          currencies=SUPPORTED_CURRENCIES,
                          default_currency=DEFAULT_CURRENCY)

@app.route('/reports')
def reports():
    return render_template('reports.html', 
                         currencies=SUPPORTED_CURRENCIES,
                         default_currency=DEFAULT_CURRENCY)

# API Endpoints
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    search_term = request.args.get('search', '').lower()
    category_filter = request.args.get('category', '')
    currency = request.args.get('currency', DEFAULT_CURRENCY)
    
    query = Transaction.query
    
    if search_term:
        query = query.filter(
            (Transaction.merchant.ilike(f'%{search_term}%')) | 
            (Transaction.description.ilike(f'%{search_term}%'))
        )
    
    if category_filter:
        query = query.filter(Transaction.category == category_filter)
        
    transactions = query.all()
    result = []
    
    for transaction in transactions:
        # Convert each transaction to dictionary
        t_dict = transaction.to_dict()
        
        # If transaction currency is different from requested currency, convert the amount
        if transaction.currency != currency:
            t_dict['original_amount'] = transaction.amount
            t_dict['original_currency'] = transaction.currency
            t_dict['amount'] = convert_currency(transaction.amount, transaction.currency, currency)
            t_dict['currency'] = currency
            
        result.append(t_dict)
        
    return jsonify(result)

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    try:
        data = request.json
        
        # Create new transaction from request data
        new_transaction = Transaction(
            date=datetime.strptime(data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d'),
            merchant=data.get('merchant', ''),
            amount=float(data.get('amount', 0)),
            currency=data.get('currency', DEFAULT_CURRENCY),
            category=data.get('category', 'Other'),
            description=data.get('description', ''),
            items=data.get('items', None)
        )
        
        db.session.add(new_transaction)
        db.session.commit()
        
        return jsonify({"success": True, "transaction": new_transaction.to_dict()})
    except Exception as e:
        logger.error(f"Error adding transaction: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    try:
        transaction = Transaction.query.get(transaction_id)
        
        if not transaction:
            return jsonify({"success": False, "error": "Transaction not found"}), 404
            
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error deleting transaction: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    try:
        data = request.json
        transaction = Transaction.query.get(transaction_id)
        
        if not transaction:
            return jsonify({"success": False, "error": "Transaction not found"}), 404
            
        # Update fields if provided
        if 'date' in data:
            transaction.date = datetime.strptime(data['date'], '%Y-%m-%d')
        if 'merchant' in data:
            transaction.merchant = data['merchant']
        if 'amount' in data:
            transaction.amount = float(data['amount'])
        if 'currency' in data:
            transaction.currency = data['currency']
        if 'category' in data:
            transaction.category = data['category']
        if 'description' in data:
            transaction.description = data['description']
        if 'items' in data:
            transaction.items = data['items']
            
        db.session.commit()
        
        return jsonify({"success": True, "transaction": transaction.to_dict()})
    except Exception as e:
        logger.error(f"Error updating transaction: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify(TRANSACTION_CATEGORIES)

@app.route('/api/currencies', methods=['GET'])
def get_currencies():
    return jsonify(SUPPORTED_CURRENCIES)

@app.route('/api/exchange-rates', methods=['GET'])
def get_exchange_rates():
    base_currency = request.args.get('base', DEFAULT_CURRENCY)
    
    try:
        rates = {}
        
        if base_currency == "USD":
            # Get rates directly from the database
            exchange_rates = ExchangeRate.query.filter_by(base_currency="USD").all()
            for rate in exchange_rates:
                rates[rate.target_currency] = rate.rate
        else:
            # Convert all rates to the requested base currency
            usd_rates = ExchangeRate.query.filter_by(base_currency="USD").all()
            
            # Find the rate for the base currency
            base_rate = next((r.rate for r in usd_rates if r.target_currency == base_currency), None)
            
            if base_rate:
                for rate in usd_rates:
                    rates[rate.target_currency] = rate.rate / base_rate
            
        # Add the base currency itself with rate 1.0
        rates[base_currency] = 1.0
        
        # Check when rates were last updated
        last_update = ExchangeRate.query.order_by(ExchangeRate.last_updated.desc()).first()
        last_updated = last_update.last_updated.strftime('%Y-%m-%d %H:%M:%S UTC') if last_update else "Never"
        
        return jsonify({
            "success": True,
            "base": base_currency,
            "rates": rates,
            "last_updated": last_updated
        })
    except Exception as e:
        logger.error(f"Error getting exchange rates: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/update-exchange-rates', methods=['POST'])
def force_update_exchange_rates():
    try:
        update_exchange_rates()
        return jsonify({"success": True, "message": "Exchange rates updated successfully"})
    except Exception as e:
        logger.error(f"Error updating exchange rates: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/process-receipt', methods=['POST'])
def process_receipt():
    try:
        if 'receipt' not in request.files:
            return jsonify({"success": False, "error": "No file part"}), 400
            
        file = request.files['receipt']
        
        if file.filename == '':
            return jsonify({"success": False, "error": "No selected file"}), 400
            
        if file:
            # Save the file with a unique name
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Create a new transaction with placeholder data
            new_transaction = Transaction(
                date=datetime.utcnow(),
                merchant="Please enter merchant name",
                amount=0.0,
                currency=DEFAULT_CURRENCY,
                category="Other",
                description="Receipt uploaded, please complete details",
                receipt_image_path=file_path
            )
            
            db.session.add(new_transaction)
            db.session.commit()
            
            # Get some financial advice using Gemini API
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                As a financial advisor, provide 3 quick tips about tracking expenses 
                and managing receipts effectively. Keep each tip under 20 words.
                Format as plain text, one tip per line.
                """
                
                response = model.generate_content(prompt)
                financial_tips = response.text
                
                return jsonify({
                    "success": True, 
                    "transaction": new_transaction.to_dict(),
                    "message": f"Receipt uploaded successfully. Please complete the transaction details.\n\nFinancial Tips:\n{financial_tips}"
                })
                
            except Exception as e:
                logger.error(f"Error getting financial tips: {str(e)}")
                # Fall back to basic confirmation
                return jsonify({
                    "success": True,
                    "transaction": new_transaction.to_dict(),
                    "message": "Receipt uploaded successfully. Please complete the transaction details."
                })
                
    except Exception as e:
        logger.error(f"Error processing receipt: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/dashboard-data', methods=['GET'])
def dashboard_data():
    try:
        currency = request.args.get('currency', DEFAULT_CURRENCY)
        
        # Get all transactions
        transactions = Transaction.query.all()
        
        # Calculate total expenses in requested currency
        total_expenses = sum(convert_currency(t.amount, t.currency, currency) for t in transactions)
        
        # Get expenses by category
        expenses_by_category = {}
        for t in transactions:
            converted_amount = convert_currency(t.amount, t.currency, currency)
            category = t.category
            if category in expenses_by_category:
                expenses_by_category[category] += converted_amount
            else:
                expenses_by_category[category] = converted_amount
        
        # Get expenses by month (for the last 6 months)
        expenses_by_month = {}
        for t in transactions:
            converted_amount = convert_currency(t.amount, t.currency, currency)
            month_key = t.date.strftime('%Y-%m')
            if month_key in expenses_by_month:
                expenses_by_month[month_key] += converted_amount
            else:
                expenses_by_month[month_key] = converted_amount
        
        # Sort by month and take last 6
        expenses_by_month = dict(sorted(expenses_by_month.items())[-6:])
        
        # Get recent transactions (last 5)
        recent_transactions = [t.to_dict() for t in 
                              Transaction.query.order_by(Transaction.date.desc()).limit(5).all()]
        
        # Convert amounts if needed
        for t in recent_transactions:
            if t['currency'] != currency:
                t['original_amount'] = t['amount']
                t['original_currency'] = t['currency']
                t['amount'] = convert_currency(t['amount'], t['currency'], currency)
                t['currency'] = currency
        
        # Top merchants by spending
        merchant_spending = {}
        for t in transactions:
            converted_amount = convert_currency(t.amount, t.currency, currency)
            merchant = t.merchant
            if merchant in merchant_spending:
                merchant_spending[merchant] += converted_amount
            else:
                merchant_spending[merchant] = converted_amount
        
        top_merchants = sorted(merchant_spending.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return jsonify({
            "success": True,
            "total_expenses": total_expenses,
            "currency": currency,
            "expenses_by_category": expenses_by_category,
            "expenses_by_month": expenses_by_month,
            "recent_transactions": recent_transactions,
            "top_merchants": [{"name": m[0], "amount": m[1]} for m in top_merchants]
        })
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/export-data', methods=['GET'])
def export_data():
    format_type = request.args.get('format', 'json')
    currency = request.args.get('currency', DEFAULT_CURRENCY)
    
    try:
        transactions = Transaction.query.all()
        
        if format_type == 'json':
            # Convert transactions to dictionaries
            result = []
            for t in transactions:
                t_dict = t.to_dict()
                if t.currency != currency:
                    t_dict['original_amount'] = t.amount
                    t_dict['original_currency'] = t.currency
                    t_dict['amount'] = convert_currency(t.amount, t.currency, currency)
                    t_dict['currency'] = currency
                result.append(t_dict)
                
            return jsonify(result)
            
        elif format_type == 'csv':
            csv_data = "id,date,merchant,amount,currency,category,description\n"
            for t in transactions:
                amount = t.amount
                curr = t.currency
                
                if t.currency != currency:
                    amount = convert_currency(t.amount, t.currency, currency)
                    curr = currency
                    
                csv_data += f"{t.id},{t.date.strftime('%Y-%m-%d')},{t.merchant},{amount},{curr},{t.category},\"{t.description or ''}\"\n"
            
            return csv_data, 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': 'attachment; filename=transactions.csv'
            }
        else:
            return jsonify({"success": False, "error": "Unsupported format"}), 400
            
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_finances():
    try:
        data = request.json
        question = data.get('question', '')
        currency = data.get('currency', DEFAULT_CURRENCY)
        
        if not question:
            return jsonify({"success": False, "error": "No question provided"}), 400
            
        # Get transactions from database
        transactions = Transaction.query.all()
        
        # Convert transactions to dictionaries with proper currency conversion
        transactions_data = []
        for t in transactions:
            t_dict = t.to_dict()
            if t.currency != currency:
                t_dict['original_amount'] = t.amount
                t_dict['original_currency'] = t.currency
                t_dict['amount'] = convert_currency(t.amount, t.currency, currency)
                t_dict['currency'] = currency
            transactions_data.append(t_dict)
            
        # Calculate total expenses in requested currency
        total_expenses = sum(t_dict['amount'] for t_dict in transactions_data)
        
        # Create a context with transaction data
        context = {
            "transactions": transactions_data,
            "total_expenses": total_expenses,
            "currency": currency,
            "categories": TRANSACTION_CATEGORIES,
            "supported_currencies": SUPPORTED_CURRENCIES
        }
        
        # Process with Gemini API
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        You are a financial analysis assistant. Answer the following question about the user's financial data.
        
        User's financial data:
        {json.dumps(context, indent=2)}
        
        User's question: {question}
        
        Provide a concise, helpful answer with any relevant insights or calculations.
        When discussing monetary amounts, always include the currency symbol.
        """
        
        response = model.generate_content(prompt)
        
        return jsonify({
            "success": True,
            "question": question,
            "answer": response.text,
            "currency": currency
        })
        
    except Exception as e:
        logger.error(f"Error analyzing finances: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
