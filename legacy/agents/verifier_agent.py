import os
import requests
import json
from typing import Dict, Any
from flask import current_app

class AgentVerifier:
    def __init__(self):
        # Gather all Gemini API keys
        self.api_keys = [
            os.getenv(f"GEMINI_API_KEY_{i}") for i in range(1, 11)
        ]
        # Always include GEMINI_API_KEY as fallback
        if os.getenv("GEMINI_API_KEY"):
            self.api_keys.append(os.getenv("GEMINI_API_KEY"))
        # Remove any None/empty
        self.api_keys = [k for k in self.api_keys if k]
        self.model = os.getenv("GEMINI_PRO_MODEL", "gemini-2.0-flash-lite")
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def verify(self, transaction: Dict[str, Any], ocr_text: str) -> Dict[str, Any]:
        prompt = f"""
You are an expert Japanese-English receipt parsing assistant.
Use chain-of-thought internally (do not output reasoning) to ensure each field is accurate.
Then output only the final JSON object matching this schema:

{{
  "corrected_transaction": {{
    "vendor": string,
    "date": "YYYY-MM-DD",
    "items": [{{"description": string, "quantity": integer, "unit_price": number}}],
    "subtotal": number,
    "tax": number,
    "tax_percentage": integer,
    "total": number,
    "currency": string,
    "address": string,
    "payment_method": string,
    "receipt_number": string,
    "phone_number": string
  }},
  "issues": [string],
  "needs_review": boolean,
  "detected_currency": string
}}

Receipt OCR text:
{ocr_text}

Extracted Transaction Data:
{transaction}

Respond strictly with the JSON object—no extra text."""
        headers = {"Content-Type": "application/json"}
        body = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]}
            ]
        }
        last_error = None
        for key in self.api_keys:
            try:
                resp = requests.post(f"{self.api_url}?key={key}", headers=headers, data=json.dumps(body), timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    # Gemini returns text in data['candidates'][0]['content']['parts'][0]['text']
                    try:
                        text = data['candidates'][0]['content']['parts'][0]['text']
                        current_app.logger.debug(f"Raw Gemini response text: {text}")
                        # Remove code fences and whitespace if present
                        cleaned = text.strip()
                        if cleaned.startswith('```json'):
                            cleaned = cleaned[len('```json'):]
                        if cleaned.startswith('```'):
                            cleaned = cleaned[len('```'):]
                        if cleaned.endswith('```'):
                            cleaned = cleaned[:-3]
                        cleaned = cleaned.strip()
                        try:
                            result = json.loads(cleaned)
                            # Fill in missing fields from original transaction, including currency fallback
                            ct = result.get('corrected_transaction', result)
                            for fld in ('currency', 'payment_method', 'receipt_number', 'phone_number'):
                                if not ct.get(fld):
                                    ct[fld] = transaction.get(fld, '')
                            result['corrected_transaction'] = ct
                        except Exception as parse_err:
                            current_app.logger.error(f"Gemini JSON parse error after cleaning: {parse_err}\nCleaned text: {cleaned}")
                            return {
                                "corrected_transaction": transaction,
                                "issues": ["Gemini response could not be parsed as JSON after cleaning."],
                                "needs_review": True
                            }
                        # If corrected_transaction is present, return it directly for UI
                        if 'corrected_transaction' in result:
                            return result
                        # Otherwise, treat the result as the corrected transaction
                        return {"corrected_transaction": result, "issues": [], "needs_review": False}
                    except Exception as parse_err:
                        return {
                            "corrected_transaction": transaction,
                            "issues": ["Gemini response could not be parsed as JSON."],
                            "needs_review": True
                        }
                else:
                    last_error = f"Gemini API error {resp.status_code}: {resp.text}"
            except Exception as e:
                last_error = str(e)
        # If all keys fail
        return {
            "corrected_transaction": transaction,
            "issues": [f"All Gemini keys failed. Last error: {last_error}"],
            "needs_review": True
        }
