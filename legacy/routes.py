import os
from flask import current_app, render_template, request, redirect, url_for, flash, jsonify, session
import logging
import json
import uuid
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import requests
from services.ocr_service import OCRService
from services.ai_service import AIService
from orchestrator import Orchestrator
orchestrator = Orchestrator()

# Import application and models
from application import db, logger, Transaction, ExchangeRate
from flask import Blueprint

main_bp = Blueprint('main', __name__)
from models import TRANSACTION_CATEGORIES, SUPPORTED_CURRENCIES, DEFAULT_CURRENCY

# Configure upload folder for receipts
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# app config and wsgi_app setup is now handled in application.py

# Currency conversion helper function
def convert_currency(amount, from_currency, to_currency):
    """Convert an amount from one currency to another using stored exchange rates"""
    if from_currency == to_currency:
        return amount
        
    # Get USD-based rates from the database
    usd_rates = {}
    rates = ExchangeRate.query.filter_by(base_currency="USD").all()
    
    for rate in rates:
        usd_rates[rate.target_currency] = rate.rate
        
    # Add USD itself
    usd_rates["USD"] = 1.0
    
    # Convert to USD first (if not already USD)
    usd_amount = amount
    if from_currency != "USD":
        usd_amount = amount / usd_rates.get(from_currency, 1.0)
        
    # Convert from USD to target currency
    return usd_amount * usd_rates.get(to_currency, 1.0)

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
                        # Create new rate
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
        db.session.rollback()

# Use a first request handler instead of before_first_request which was removed in Flask 2.3+
@main_bp.before_app_request
def initialize_app():
    # We'll use this request handler flag to run once
    from flask import current_app
    if getattr(current_app, '_exchange_rates_initialized', False):
        return 
    
    # Update exchange rates the first time 
    update_exchange_rates()
    current_app._exchange_rates_initialized = True

# Routes
@main_bp.route('/')
def index():
    update_exchange_rates()
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', 
                          currencies=SUPPORTED_CURRENCIES,
                          current_currency=session.get('currency', DEFAULT_CURRENCY))

@main_bp.route('/upload')
def upload():
    return render_template('upload.html',
                          categories=TRANSACTION_CATEGORIES,
                          currencies=SUPPORTED_CURRENCIES,
                          current_currency=session.get('currency', DEFAULT_CURRENCY),
                          default_currency=DEFAULT_CURRENCY)

@main_bp.route('/transactions')
def transactions():
    return render_template('transactions.html', 
                          categories=TRANSACTION_CATEGORIES,
                          currencies=SUPPORTED_CURRENCIES,
                          current_currency=session.get('currency', DEFAULT_CURRENCY))

@main_bp.route('/reports')
def reports():
    return render_template('reports.html', 
                          currencies=SUPPORTED_CURRENCIES,
                          current_currency=session.get('currency', DEFAULT_CURRENCY))

# API Routes
@main_bp.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        logger.info("Attempting to get all transactions")
        # Get all transactions ordered by date descending
        try:
            logger.info("Querying Transaction model")
            transactions = Transaction.query.order_by(Transaction.date.desc()).all()
            logger.info(f"Found {len(transactions)} transactions")
        except Exception as query_error:
            logger.error(f"Failed to query transactions: {str(query_error)}")
            return jsonify({"error": f"Database query failed: {str(query_error)}"}), 500
            
        # Get desired currency for conversion
        currency = request.args.get('currency', DEFAULT_CURRENCY)
        
        result = []
        
        # Format data for response
        for t in transactions:
            try:
                t_dict = t.to_dict()
                # Convert to desired currency if needed
                if currency != t_dict['currency']:
                    t_dict['original_amount'] = t_dict['amount']
                    t_dict['original_currency'] = t_dict['currency']
                    t_dict['amount'] = convert_currency(t_dict['amount'], t_dict['currency'], currency)
                    t_dict['currency'] = currency
                result.append(t_dict)
            except Exception as dict_error:
                logger.error(f"Failed to convert transaction to dict: {str(dict_error)}")
                # Continue with other transactions
        
        logger.info(f"Successfully returning {len(result)} transactions")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@main_bp.route('/api/transactions', methods=['POST'])
def add_transaction():
    try:
        logger.info("Starting add_transaction endpoint")
        data = request.json
        logger.info(f"Received transaction data: {json.dumps(data, default=str)}")

        # Set default date if not provided
        if 'date' not in data or not data.get('date'):
            date_val = datetime.now()
            logger.info(f"Using default date: {date_val}")
        else:
            try:
                date_val = datetime.strptime(data.get('date'), '%Y-%m-%d')
                logger.info(f"Parsed date: {date_val}")
            except ValueError as e:
                logger.error(f"Invalid date format: {data.get('date')}")
                return jsonify({"success": False, "error": f"Invalid date format: {str(e)}"}), 400

        # Ensure all required fields are present with safe defaults
        merchant = data.get('merchant', 'Unknown Merchant')
        try:
            amount = float(data.get('amount', 0))
        except Exception:
            logger.error(f"Invalid amount: {data.get('amount')}")
            return jsonify({"success": False, "error": "Invalid amount provided."}), 400
        currency = data.get('currency', DEFAULT_CURRENCY)
        category = data.get('category', 'Other')
        description = data.get('description', f'Purchase from {merchant}')
        items = data.get('items', None)
        # Serialize items as JSON string if it's a list (SQLite does not support lists)
        if items is not None and not isinstance(items, str):
            try:
                items = json.dumps(items)
            except Exception as e:
                logger.error(f"Failed to serialize items: {items}. Error: {e}")
                items = "[]"
        receipt_data = data.get('receipt_data', None)
        shop_name = data.get('shop_name', None)
        tax = data.get('tax', None)
        payment_method = data.get('payment_method', None)
        receipt_number = data.get('receipt_number', None)
        address = data.get('address', None)
        phone_number = data.get('phone_number', None)
        notes = data.get('notes', None)

        try:
            logger.info("Creating new Transaction object")
            new_transaction = Transaction(
                date=date_val,
                merchant=merchant,
                amount=amount,
                currency=currency,
                category=category,
                description=description,
                items=items,
                receipt_data=receipt_data,
                shop_name=shop_name,
                tax=tax,
                payment_method=payment_method,
                receipt_number=receipt_number,
                address=address,
                phone_number=phone_number,
                notes=notes
            )
            logger.info("Transaction object created successfully")
        except Exception as create_error:
            logger.error(f"Failed to create Transaction object: {str(create_error)} | Payload: {json.dumps(data, default=str)}")
            return jsonify({"success": False, "error": f"Failed to create transaction: {str(create_error)}"}), 400
        
        # Explicitly commit to database with error handling
        try:
            logger.info(f"Adding transaction to database: {new_transaction.merchant}, {new_transaction.amount} {new_transaction.currency}")
            db.session.add(new_transaction)
            logger.info("Transaction added to session")
            db.session.commit()
            logger.info(f"Transaction committed successfully with ID: {new_transaction.id}")
        except Exception as db_error:
            logger.error(f"Database error when adding transaction: {str(db_error)}")
            db.session.rollback()
            logger.info("Session rolled back due to error")
            return jsonify({"success": False, "error": f"Database error: {str(db_error)}"}), 500
        
        # Return the created transaction
        try:
            result = new_transaction.to_dict()
            logger.info("Transaction converted to dict successfully")
            return jsonify({"success": True, "transaction": result})
        except Exception as dict_error:
            logger.error(f"Error converting transaction to dict: {str(dict_error)}")
            return jsonify({"success": True, "message": "Transaction saved but failed to format response"}), 200
    except Exception as e:
        logger.error(f"Unexpected error adding transaction: {str(e)}")
        if 'db_session' in locals():
            db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@main_bp.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    try:
        logger.info(f"Attempting to delete transaction with ID: {transaction_id}")
        transaction = Transaction.query.get(transaction_id)
        
        if not transaction:
            logger.warning(f"Transaction with ID {transaction_id} not found for deletion")
            return jsonify({"success": False, "error": "Transaction not found"}), 404
            
        # Log transaction details before deletion for debugging
        logger.info(f"Deleting transaction: {transaction.merchant}, {transaction.amount} {transaction.currency}")
        
        # Delete the transaction
        db.session.delete(transaction)
        db.session.commit()
        
        logger.info(f"Transaction with ID {transaction_id} successfully deleted")
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error deleting transaction {transaction_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@main_bp.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    try:
        data = request.json
        logger.info(f"Updating transaction {transaction_id} with data: {data}")
        
        transaction = Transaction.query.get(transaction_id)
        
        if not transaction:
            logger.warning(f"Transaction with ID {transaction_id} not found for update")
            return jsonify({"success": False, "error": "Transaction not found"}), 404
            
        # Log original transaction details
        logger.info(f"Original transaction: {transaction.merchant}, {transaction.amount} {transaction.currency}")
        
        # Update fields if provided
        if 'date' in data and data['date']:
            try:
                transaction.date = datetime.strptime(data['date'], '%Y-%m-%d')
            except ValueError as date_error:
                logger.error(f"Invalid date format in update: {data['date']}")
                return jsonify({"success": False, "error": f"Invalid date format: {str(date_error)}"}), 400
                
        if 'merchant' in data:
            transaction.merchant = data['merchant']
        if 'amount' in data:
            try:
                transaction.amount = float(data['amount'])
            except ValueError:
                logger.error(f"Invalid amount in update: {data['amount']}")
                return jsonify({"success": False, "error": "Amount must be a valid number"}), 400
                
        if 'currency' in data:
            transaction.currency = data['currency']
        if 'category' in data:
            transaction.category = data['category']
        if 'description' in data:
            transaction.description = data['description']
        if 'items' in data:
            transaction.items = data['items']
            
        # Commit changes to database with error handling
        try:
            db.session.commit()
            logger.info(f"Transaction {transaction_id} updated successfully")
        except Exception as db_error:
            db.session.rollback()
            logger.error(f"Database error when updating transaction: {str(db_error)}")
            raise db_error
        
        # Return updated transaction
        result = transaction.to_dict()
        logger.info(f"Updated transaction: {result}")
        return jsonify({"success": True, "transaction": result})
    except Exception as e:
        logger.error(f"Error updating transaction {transaction_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@main_bp.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify(TRANSACTION_CATEGORIES)

@main_bp.route('/api/currencies', methods=['GET'])
def get_currencies():
    return jsonify(SUPPORTED_CURRENCIES)

@main_bp.route('/api/exchange-rates', methods=['GET'])
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

@main_bp.route('/api/update-exchange-rates', methods=['POST'])
def force_update_exchange_rates():
    try:
        update_exchange_rates()
        return jsonify({"success": True, "message": "Exchange rates updated successfully"})
    except Exception as e:
        logger.error(f"Error updating exchange rates: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@main_bp.route('/api/process-receipt', methods=['POST'])
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
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Delegate to orchestrator for full processing and wrap in API response
            target_currency = request.form.get('currency', DEFAULT_CURRENCY)
            confirmed = orchestrator.process_receipt(file_path, target_currency)
            
            # Normalize transaction fields for frontend
            normalized = {
                "merchant": confirmed.get("vendor", ""),
                "amount": confirmed.get("total", 0),
                "currency": confirmed.get("currency", DEFAULT_CURRENCY),
                "category": confirmed.get("category", ""),
                "description": confirmed.get("description", confirmed.get("note", "")),
                # Normalize date format to YYYY-MM-DD for date input compatibility
                "date": (confirmed.get("date", "").replace('/', '-') if confirmed.get("date") else ""),
                "shop_name": confirmed.get("shop_name", ""),
                "items": [
                    {"name": item.get("description", ""), "quantity": item.get("quantity", 0), "price": item.get("unit_price", 0)}
                    for item in confirmed.get("items", [])
                ],
                "tax": confirmed.get("tax", 0),
                "payment_method": confirmed.get("payment_method", ""),
                "receipt_number": confirmed.get("receipt_number", ""),
                "address": confirmed.get("address", ""),
                "phone_number": confirmed.get("phone_number", ""),
                "notes": confirmed.get("note", ""),
                "receipt_data": confirmed.get("receipt_data", "")
            }
            return jsonify({"success": True, "transaction": normalized})
    except Exception as e:
        logger.error(f"Error processing receipt: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@main_bp.route('/api/dashboard-data', methods=['GET'])
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

@main_bp.route('/api/export-data', methods=['GET'])
def export_data():
    format_type = request.args.get('format', 'json')
    currency = request.args.get('currency', DEFAULT_CURRENCY)
    
    try:
        transactions = Transaction.query.all()
        
        if format_type == 'json':
            # Export as JSON
            result = []
            for t in transactions:
                t_dict = t.to_dict()
                
                # Convert amount if needed
                if t.currency != currency:
                    t_dict['original_amount'] = t_dict['amount']
                    t_dict['original_currency'] = t_dict['currency']
                    t_dict['amount'] = convert_currency(t.amount, t.currency, currency)
                    t_dict['currency'] = currency
                    
                result.append(t_dict)
                
            return jsonify(result)
            
        elif format_type == 'csv':
            # Export as CSV
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['ID', 'Date', 'Merchant', 'Amount', 'Currency', 'Category', 'Description'])
            
            # Write data
            for t in transactions:
                amount = t.amount
                curr = t.currency
                
                # Convert if needed
                if t.currency != currency:
                    amount = convert_currency(t.amount, t.currency, currency)
                    curr = currency
                    
                writer.writerow([
                    t.id,
                    t.date.strftime('%Y-%m-%d'),
                    t.merchant,
                    amount,
                    curr,
                    t.category,
                    t.description or ""
                ])
                
            return output.getvalue(), 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': 'attachment; filename=transactions.csv'
            }
            
        else:
            return jsonify({"success": False, "error": "Unsupported format"}), 400
            
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@main_bp.route('/api/analyze-finances', methods=['POST'])
def analyze_finances():
    try:
        data = request.json
        question = data.get('question', '')
        currency = data.get('currency', DEFAULT_CURRENCY)
        
        if not question:
            return jsonify({"success": False, "error": "No question provided"}), 400
            
        # Get all transactions for analysis
        transactions = Transaction.query.all()
        
        # Prepare transaction data for the AI
        transaction_data = []
        for t in transactions:
            amount = convert_currency(t.amount, t.currency, currency)
            
            transaction_data.append({
                "date": t.date.strftime('%Y-%m-%d'),
                "merchant": t.merchant,
                "amount": amount,
                "currency": currency,
                "category": t.category
            })
            
        # Create a context for Gemini to analyze
        context = {
            "transactions": transaction_data,
            "currency": currency,
            "question": question
        }
        
        context_str = json.dumps(context, indent=2)
        
        # Use Gemini to analyze the data
        try:
            model = AIService.get_model('gemini-1.5-flash')
            prompt = f"""
            You are a financial advisor analyzing a set of financial transactions.
            Please answer the following question based on the provided transaction data.
            Focus on providing insights, trends, and patterns relevant to the question.
            
            Transaction Data:
            {context_str}
            
            Question: {question}
            
            Provide a detailed but concise response with bullet points where appropriate.
            Include specific figures and percentages to support your analysis.
            """
            
            response = AIService.generate_content(prompt)
            
            return jsonify({
                "success": True,
                "answer": response.text
            })
            
        except Exception as e:
            logger.error(f"Error generating AI analysis: {str(e)}")
            return jsonify({
                "success": False, 
                "error": "Unable to generate analysis. Please try again later."
            }), 500
            
    except Exception as e:
        logger.error(f"Error analyzing finances: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Alias for legacy AI endpoint to support dashboard
@main_bp.route('/api/analyze', methods=['POST'])
def analyze_legacy():
    return analyze_finances()