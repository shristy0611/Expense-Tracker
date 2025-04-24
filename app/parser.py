import re

def parse_with_regex(text: str) -> dict:
    """
    Simple regex-based extraction of merchant, date, and total fields from OCR text.
    Merchant: first non-empty line.
    Date: ISO or YYYY/MM/DD patterns.
    Total: 'Total' label followed by amount.
    """
    # Merchant: first non-empty line
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    merchant = lines[0] if lines else None

    # Date pattern YYYY-MM-DD or YYYY/MM/DD
    date_match = re.search(r"\b(\d{4}[/-]\d{2}[/-]\d{2})\b", text)
    date = date_match.group(1) if date_match else None

    # Total amount pattern after 'Total'
    # Allow $ or ¥ currency symbols
    total_match = re.search(r"\b[Tt]otal[:\s]*[\$\u00A5]?\s*([0-9]+(?:\.[0-9]{2}))\b", text)
    total = total_match.group(1) if total_match else None

    return {"merchant": merchant, "date": date, "total": total}
