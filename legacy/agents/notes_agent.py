import os
import requests
import json
from typing import Dict, Any

class AgentNotes:
    def __init__(self):
        self.api_keys = [
            os.getenv(f"GEMINI_API_KEY_{i}") for i in range(1, 11)
        ]
        if os.getenv("GEMINI_API_KEY"):
            self.api_keys.append(os.getenv("GEMINI_API_KEY"))
        self.api_keys = [k for k in self.api_keys if k]
        self.model = os.getenv("GEMINI_PRO_MODEL", "gemini-2.0-flash-lite")
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def generate(self, transaction: Dict[str, Any], ocr_text: str) -> Dict[str, Any]:
        prompt = f"""
You are an expert financial assistant. Given the following receipt OCR text and extracted transaction data, do the following:
- Suggest the most likely category for the transaction (e.g., Groceries, Dining Out, Electronics, Pet Supplies, etc.).
- Generate a short, human-readable summary note for the transaction, mentioning the merchant, main items or purpose, and any special context (e.g., coupon applied).

Receipt OCR text:
{ocr_text}

Extracted Transaction Data:
{transaction}

Return a JSON object with keys: category (string), note (string).
"""
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
                    try:
                        text = data['candidates'][0]['content']['parts'][0]['text']
                        result = json.loads(text)
                        return result
                    except Exception as parse_err:
                        return {"category": "Uncategorized", "note": "Could not parse Gemini response."}
                else:
                    last_error = f"Gemini API error {resp.status_code}: {resp.text}"
            except Exception as e:
                last_error = str(e)
        return {"category": "Uncategorized", "note": f"All Gemini keys failed. Last error: {last_error}"}
