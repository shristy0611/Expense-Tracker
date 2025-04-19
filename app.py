import os
import logging
import json
import base64
import io
from datetime import datetime
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

# Configure Google Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "your-gemini-api-key"))

# In-memory storage for MVP
TRANSACTIONS = []
CATEGORIES = [
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

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload')
def upload():
    return render_template('upload.html', categories=CATEGORIES)

@app.route('/transactions')
def transactions():
    return render_template('transactions.html', categories=CATEGORIES)

@app.route('/reports')
def reports():
    return render_template('reports.html')

# API Endpoints
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    search_term = request.args.get('search', '').lower()
    category_filter = request.args.get('category', '')
    
    filtered_transactions = TRANSACTIONS
    
    if search_term:
        filtered_transactions = [t for t in filtered_transactions if 
                                search_term in t['merchant'].lower() or 
                                search_term in t['description'].lower()]
    
    if category_filter:
        filtered_transactions = [t for t in filtered_transactions if 
                                t['category'] == category_filter]
        
    return jsonify(filtered_transactions)

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    try:
        data = request.json
        data['id'] = len(TRANSACTIONS) + 1
        data['date'] = datetime.now().strftime('%Y-%m-%d')
        TRANSACTIONS.append(data)
        return jsonify({"success": True, "transaction": data})
    except Exception as e:
        logger.error(f"Error adding transaction: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    global TRANSACTIONS
    try:
        TRANSACTIONS = [t for t in TRANSACTIONS if t['id'] != transaction_id]
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error deleting transaction: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    try:
        data = request.json
        for i, transaction in enumerate(TRANSACTIONS):
            if transaction['id'] == transaction_id:
                TRANSACTIONS[i].update(data)
                return jsonify({"success": True, "transaction": TRANSACTIONS[i]})
        return jsonify({"success": False, "error": "Transaction not found"}), 404
    except Exception as e:
        logger.error(f"Error updating transaction: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify(CATEGORIES)

@app.route('/api/process-receipt', methods=['POST'])
def process_receipt():
    try:
        if 'receipt' not in request.files:
            return jsonify({"success": False, "error": "No file part"}), 400
            
        file = request.files['receipt']
        
        if file.filename == '':
            return jsonify({"success": False, "error": "No selected file"}), 400
            
        if file:
            # Read the file content but don't process it with OCR
            content = file.read()
            
            # Create a placeholder transaction with example data
            new_transaction = {
                "id": len(TRANSACTIONS) + 1,
                "date": datetime.now().strftime('%Y-%m-%d'),
                "merchant": "Sample Merchant",
                "amount": 0.00,
                "category": "Other",
                "description": "Please review and update the transaction details",
                "items": []
            }
            
            # Here, we would normally analyze the receipt with AI
            # But for now we'll just use the Gemini API to recommend tips
            try:
                # Get some general tips about financial management using Gemini
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
                    "transaction": new_transaction,
                    "raw_text": f"Receipt uploaded successfully. Please enter the transaction details manually.\n\nFinancial Tips:\n{financial_tips}"
                })
                
            except Exception as e:
                logger.error(f"Error getting financial tips: {str(e)}")
                # Fall back to basic confirmation
                return jsonify({
                    "success": True,
                    "transaction": new_transaction,
                    "raw_text": "Receipt uploaded successfully. Please enter the transaction details manually."
                })
                
    except Exception as e:
        logger.error(f"Error processing receipt: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/dashboard-data', methods=['GET'])
def dashboard_data():
    try:
        # Calculate total expenses
        total_expenses = sum(t['amount'] for t in TRANSACTIONS)
        
        # Get expenses by category
        expenses_by_category = {}
        for t in TRANSACTIONS:
            category = t['category']
            if category in expenses_by_category:
                expenses_by_category[category] += t['amount']
            else:
                expenses_by_category[category] = t['amount']
        
        # Get expenses by month (for the last 6 months)
        expenses_by_month = {}
        for t in TRANSACTIONS:
            date = datetime.strptime(t['date'], '%Y-%m-%d')
            month_key = date.strftime('%Y-%m')
            if month_key in expenses_by_month:
                expenses_by_month[month_key] += t['amount']
            else:
                expenses_by_month[month_key] = t['amount']
        
        # Get recent transactions (last 5)
        recent_transactions = sorted(TRANSACTIONS, key=lambda x: x['date'], reverse=True)[:5]
        
        # Top merchants by spending
        merchant_spending = {}
        for t in TRANSACTIONS:
            merchant = t['merchant']
            if merchant in merchant_spending:
                merchant_spending[merchant] += t['amount']
            else:
                merchant_spending[merchant] = t['amount']
        
        top_merchants = sorted(merchant_spending.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return jsonify({
            "success": True,
            "total_expenses": total_expenses,
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
    
    if format_type == 'json':
        return jsonify(TRANSACTIONS)
    elif format_type == 'csv':
        csv_data = "id,date,merchant,amount,category,description\n"
        for t in TRANSACTIONS:
            csv_data += f"{t['id']},{t['date']},{t['merchant']},{t['amount']},{t['category']},\"{t['description']}\"\n"
        
        return csv_data, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=transactions.csv'
        }
    else:
        return jsonify({"success": False, "error": "Unsupported format"}), 400

@app.route('/api/analyze', methods=['POST'])
def analyze_finances():
    try:
        data = request.json
        question = data.get('question', '')
        
        if not question:
            return jsonify({"success": False, "error": "No question provided"}), 400
            
        # Create a context with transaction data
        context = {
            "transactions": TRANSACTIONS,
            "total_expenses": sum(t['amount'] for t in TRANSACTIONS),
            "categories": CATEGORIES
        }
        
        # Process with Gemini API
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        You are a financial analysis assistant. Answer the following question about the user's financial data.
        
        User's financial data:
        {json.dumps(context, indent=2)}
        
        User's question: {question}
        
        Provide a concise, helpful answer with any relevant insights or calculations.
        """
        
        response = model.generate_content(prompt)
        
        return jsonify({
            "success": True,
            "question": question,
            "answer": response.text
        })
        
    except Exception as e:
        logger.error(f"Error analyzing finances: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
