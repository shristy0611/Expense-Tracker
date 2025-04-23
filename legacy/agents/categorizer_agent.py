from typing import Dict, Any, List
import re
import json
import logging
logger = logging.getLogger(__name__)
from services.ai_service import AIService
from flask import current_app
from services.rag_service import RAGService

class AgentCategorizer:
    def parse(self, ocr_json: Dict[str, Any]) -> Dict[str, Any]:
        # Use AI-refined text if available, else raw segments
        text = ocr_json.get('cleaned_text', ' '.join(seg['text'] for seg in ocr_json['segments']))
        # Fallback: shop name often on second line
        lines = text.split('\n')
        shop_name_fallback = lines[1].strip() if len(lines) > 1 else ''
        # Compute fallback for contact/payment fields
        phone_match = re.search(r'\b\d{2,4}-\d{1,4}-\d{3,4}\b', text)
        phone_fallback = phone_match.group(0) if phone_match else ''
        payment_match = re.search(r'(?:VISA|MasterCard|American Express|AMEX|Credit Card)', text, re.IGNORECASE)
        payment_fallback = payment_match.group(0) if payment_match else ''
        receipt_match = re.search(r'(?:Receipt|レシート)\s*#?\s*([A-Za-z0-9\-]+)', text, re.IGNORECASE)
        receipt_fallback = receipt_match.group(1) if receipt_match else ''
        # RAG context retrieval for SOTA RAG
        try:
            RAGService.initialize()
            retrieved = RAGService.retrieve(text, k=current_app.config.get("RAG_K", 5))
        except Exception as rag_err:
            logger.error(f"RAG retrieval failed: {rag_err}")
            retrieved = []
        context_str = "Context from similar receipts:\n" + "\n".join(f"- {r}" for r in retrieved) + "\n\n"
        # AI-based parsing using Gemini
        try:
            prompt = (
                context_str + "Parse the receipt text below into JSON with keys:\n"
                "vendor (string), shop_name (string), date (YYYY-MM-DD), items (list of {description: string, quantity: int, unit_price: number}),\n"
                "subtotal (number), tax (number), tax_percentage (integer), total (number), currency (string), address (string).\n"
                "Return only the JSON object without extra text.\n"
                f"Receipt Text:\n{text}"
            )
            response = AIService.generate_content(prompt)
            raw = response.text if hasattr(response, 'text') else str(response)
            cleaned = raw.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[len('```json'):]
            if cleaned.startswith('```'):
                cleaned = cleaned[len('```'):]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            parsed = json.loads(cleaned)
            # Merge fallback values if missing
            parsed.setdefault('shop_name', shop_name_fallback)
            parsed.setdefault('phone_number', phone_fallback)
            parsed.setdefault('payment_method', payment_fallback)
            parsed.setdefault('receipt_number', receipt_fallback)
            return parsed
        except Exception as e:
            logger.error(f"Categorizer LLM parse error: {e}")
        # Fallback to simple pattern extraction including payment and contact
        vendor = re.search(r'LAWSON|ローソン', text, re.IGNORECASE)
        date = re.search(r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})', text)
        total = re.search(r'合計\s*¥?(\d+)', text)
        items = []
        for line in text.split('\n'):
            # Match description, quantity and price (decimal, optional negative via trailing '-')
            m = re.match(r'(.*?)\s+(\d+(?:\.\d+)?)\s*¥?(-?\d+(?:\.\d+)?)-?', line)
            if m:
                desc = m.group(1).strip()
                qty = float(m.group(2))
                price = float(m.group(3))
                # If line ends with '-', treat as discount
                if line.strip().endswith('-'):
                    price = -abs(price)
                items.append({
                    'description': desc,
                    'quantity': qty,
                    'unit_price': price
                })
        # Fallback: shop name using fallback value
        shop_name = shop_name_fallback
        subtotal = sum(i['quantity'] * i['unit_price'] for i in items)
        tax = 0  # Extraction omitted for brevity
        currency = 'JPY'
        result = {
            'vendor': vendor.group(0) if vendor else '',
            'shop_name': shop_name,
            'date': date.group(1) if date else '',
            'items': items,
            'subtotal': subtotal,
            'tax': tax,
            'tax_percentage': 8,
            'total': int(total.group(1)) if total else subtotal,
            'currency': currency,
            'address': '',
            'payment_method': '',
            'receipt_number': '',
            'phone_number': '',
            'needs_review': False
        }
        if subtotal + tax != result['total']:
            result['needs_review'] = True
        return result
