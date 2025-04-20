import threading
import google.generativeai as genai
from flask import current_app

class AIService:
    """Service for rotating Gemini API keys and generating AI content."""
    _lock = threading.Lock()
    _index = 0

    @classmethod
    def generate_financial_tips(cls, prompt: str) -> str:
        # Rotate through configured API keys
        keys = current_app.config.get("GEMINI_API_KEYS", [])
        if not keys:
            raise RuntimeError("No Gemini API keys configured")
        with cls._lock:
            key = keys[cls._index % len(keys)]
            cls._index += 1
        genai.configure(api_key=key)
        model_name = current_app.config.get("GEMINI_MODEL_NAME", "gemini-2.0-flash-lite")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
