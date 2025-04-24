import os
import json
from PIL import Image
import pytesseract
import cv2
import numpy as np
import openai

# Configure OpenAI (Gemini) API
openai.api_key = os.getenv('GEMINI_API_KEY')
MODEL = os.getenv('GEMINI_PRO_MODEL')

# Supported languages: English (eng) and Japanese (jpn)
TESS_LANG = 'eng+jpn'


def preprocess_image(file_path: str) -> np.ndarray:
    """
    Load image, convert to grayscale, upscale, denoise, and threshold.
    """
    img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    # Upscale for better recognition
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    # Reduce noise while preserving edges
    img = cv2.bilateralFilter(img, 9, 75, 75)
    # Binarize image
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return img


def ocr_extract(file_path: str) -> str:
    """
    Run Tesseract OCR on the given file and return raw text.
    Supports English and Japanese.
    """
    # Preprocess and extract text
    try:
        img = preprocess_image(file_path)
    except Exception:
        # Fallback to PIL
        img = Image.open(file_path)
    text = pytesseract.image_to_string(img, lang=TESS_LANG, config='--oem 1 --psm 6')
    return text


def parse_receipt_fields(ocr_text: str) -> dict:
    """
    Use LLM to parse merchant, date, and total from OCR text.
    Returns a dict: {merchant, date, total}.
    """
    prompt = (
        "Extract merchant name, date (YYYY-MM-DD), and total amount as JSON from the receipt text. "
        f"Text:\n```{ocr_text}```"
    )
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a receipt parsing assistant with high accuracy."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )
    content = response.choices[0].message.content
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = {"merchant": None, "date": None, "total": None}
    return data
