import pytesseract
from PIL import Image, ImageEnhance
import base64
import json
from services.ai_service import AIService

class OCRService:
    """Service for OCR extraction and parsing using Tesseract and LLM refinement."""

    @staticmethod
    def extract_text(image_path: str) -> str:
        """Extract raw text from image using Tesseract OCR for English and Japanese."""
        img = Image.open(image_path)
        # Enhance contrast to improve OCR accuracy
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        # Convert to grayscale
        img = img.convert('L')
        # Perform OCR with LSTM engine and auto page segmentation
        text = pytesseract.image_to_string(img, lang='eng+jpn', config='--oem 1 --psm 3')
        if text and text.strip():
            # Prevent placeholder sample text
            if text.strip() == "Sample receipt content would appear here.":
                return ""
            return text

        # Fallback to LLM-only OCR
        llm_text = OCRService.extract_text_with_llm(image_path)
        if llm_text and llm_text.strip() == "Sample receipt content would appear here.":
            return ""
        return llm_text

    @staticmethod
    def extract_text_with_llm(image_path: str) -> str:
        """Fallback OCR using Gemini LLM API only."""
        with open(image_path, 'rb') as f:
            img_data = f.read()
        b64 = base64.b64encode(img_data).decode('utf-8')
        prompt = (
            "You are an OCR assistant. Extract all visible text from the following base64-encoded receipt image. "
            "Return plain text output, preserving lines:\n"
            + b64
        )
        return AIService.generate_financial_tips(prompt)

    @staticmethod
    def parse_receipt(text: str) -> dict:
        """Parse raw OCR text into structured receipt data via LLM."""
        prompt = (
            "Extract the following fields from the receipt text and output valid JSON with keys: "
            "merchant, date (YYYY-MM-DD), total_amount, currency, category, description, "
            "items (list of {\"name\", \"quantity\", \"price\"}), tax, payment_method, "
            "receipt_number, shop_name, address, phone_number, notes.\n"
            "If you are not confident about a field (such as merchant or description), return an empty string (\"\") or null. Do NOT use placeholders like 'Sample Store' or 'Receipt processed automatically'.\n"
            "Receipt text:\n```\n" + text + "\n```"
        )
        response = AIService.generate_financial_tips(prompt)
        import logging
        logging.info(f"[OCRService] Raw OCR text: {text}")
        logging.info(f"[OCRService] LLM parsed response: {response}")
        try:
            # Strip all backticks and trim whitespace
            cleaned = response.replace('`', '').strip()
            # Extract JSON substring between first '{' and last '}'
            start = cleaned.find('{')
            end = cleaned.rfind('}')
            if start != -1 and end != -1:
                json_str = cleaned[start:end+1]
                return json.loads(json_str)
            # Fallback: parse entire cleaned string
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logging.error(f"[OCRService] Failed to parse LLM JSON: {response}")
            return {}
