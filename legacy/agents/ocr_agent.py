from typing import Dict, Any
import pytesseract
import json
from flask import current_app
from services.ai_service import AIService
from PIL import Image

class AgentOCR:
    def process(self, image_path: str) -> Dict[str, Any]:
        img = Image.open(image_path)
        data = pytesseract.image_to_data(img, lang='eng+jpn', output_type=pytesseract.Output.DICT)
        segments = []
        for i, text in enumerate(data['text']):
            if text.strip():
                segments.append({
                    "text": text,
                    "confidence": float(data['conf'][i]) if data['conf'][i] != '-1' else 0.0
                })
        low_conf = [seg for seg in segments if seg['confidence'] < 60]
        # Use raw Tesseract output for refinement
        raw_text = pytesseract.image_to_string(img, lang='eng+jpn')
        # Refine raw OCR text via Gemini
        try:
            prompt = (
                "Refine the OCR output text below from a receipt, correcting errors while preserving original line breaks. "
                "Return JSON with keys clean_text (string) and blocks (list of paragraph strings). Only output JSON."
                f"\nRaw OCR text:\n{raw_text}"
            )
            response = AIService.generate_content(prompt)
            refined = response.text if hasattr(response, 'text') else str(response)
            current_app.logger.debug(f"Raw OCR refine response: {refined}")
            cleaned = refined.strip()
            current_app.logger.debug(f"Cleaned OCR refine JSON: {cleaned}")
            if cleaned.startswith('```json'):
                cleaned = cleaned[len('```json'):]
            if cleaned.startswith('```'):
                cleaned = cleaned[len('```'):]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            result = json.loads(cleaned)
            clean_text = result.get('clean_text', raw_text)
        except Exception as e:
            current_app.logger.error(f"Failed refining OCR: {e}")
            clean_text = raw_text
        return {
            "segments": segments,
            "cleaned_text": clean_text,
            "flagged_for_review": bool(low_conf),
            "low_confidence_segments": low_conf
        }
