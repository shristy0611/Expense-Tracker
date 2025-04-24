import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Receipt
from app.schemas import ReceiptSchema
import datetime
import re
from app.ocr import ocr_extract, parse_receipt_fields
from app.parser import parse_with_regex

# Blueprints
upload_bp = Blueprint('upload', __name__)
receipts_bp = Blueprint('receipts', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['POST'])
def upload_receipt():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        # Parse optional notes/tags from form
        notes = request.form.get('notes')
        tags_raw = request.form.get('tags')
        tags = None
        if tags_raw:
            # Accept comma-separated only (do not split on spaces)
            tags = ','.join([t.strip() for t in tags_raw.split(',') if t.strip()])
        # Create DB record and parse fields
        receipt = Receipt(filename=filename, notes=notes, tags=tags)
        db.session.add(receipt)
        db.session.commit()
        try:
            raw_text = ocr_extract(file_path)
            parsed = parse_receipt_fields(raw_text)
            # Fallback regex parsing for missing fields
            if not all([parsed.get('merchant'), parsed.get('date'), parsed.get('total')]):
                regexed = parse_with_regex(raw_text)
                parsed = {k: parsed.get(k) or regexed.get(k) for k in ['merchant', 'date', 'total']}
            if parsed.get('merchant'):
                receipt.merchant = parsed['merchant']
            if parsed.get('date'):
                receipt.date = datetime.date.fromisoformat(parsed['date'])
            if parsed.get('total'):
                receipt.total = float(parsed['total'])
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"OCR parsing failed: {e}")
        schema = ReceiptSchema()
        return schema.jsonify(receipt), 201
    return jsonify({'error': 'File type not allowed'}), 400

@receipts_bp.route('/receipts', methods=['GET'])
def list_receipts():
    # Pagination params
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    q = Receipt.query.order_by(Receipt.created_at.desc())
    paginated = q.paginate(page=page, per_page=per_page, error_out=False)
    schema = ReceiptSchema(many=True)
    return jsonify({
        'receipts': schema.dump(paginated.items),
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })

@receipts_bp.route('/receipts/<int:receipt_id>', methods=['GET'])
def get_receipt(receipt_id):
    receipt = Receipt.query.get_or_404(receipt_id)
    schema = ReceiptSchema()
    return schema.jsonify(receipt), 200
