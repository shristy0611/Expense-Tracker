from agents.ocr_agent import AgentOCR
from agents.categorizer_agent import AgentCategorizer
from agents.currency_agent import AgentCurrency
from agents.confirmation_agent import AgentConfirmation
from agents.report_agent import AgentReport
from agents.verifier_agent import AgentVerifier
from agents.notes_agent import AgentNotes
from models import TRANSACTION_CATEGORIES

class Orchestrator:
    def __init__(self):
        self.ocr = AgentOCR()
        self.categorizer = AgentCategorizer()
        self.currency = AgentCurrency()
        self.verifier = AgentVerifier()
        self.notes = AgentNotes()
        self.confirmation = AgentConfirmation()
        self.report = AgentReport()

    def process_receipt(self, image_path, target_currency='JPY'):
        ocr_result = self.ocr.process(image_path)
        categorized = self.categorizer.parse(ocr_result)
        # LLM-based verification/correction using AI-refined text if available
        full_text = ocr_result.get('cleaned_text', ' '.join(seg['text'] for seg in ocr_result['segments']))
        verification = self.verifier.verify(categorized, full_text)
        corrected = verification.get('corrected_transaction', categorized)
        # Add raw OCR text for UI prefill
        corrected['receipt_data'] = full_text
        # If LLM says needs review, set flag
        if verification.get('needs_review'):
            corrected['needs_review'] = True
            corrected['issues'] = verification.get('issues', [])
        # Use detected_currency if provided and different from user-selected
        detected_currency = verification.get('detected_currency', corrected.get('currency', target_currency))
        if detected_currency != target_currency:
            corrected['currency_flagged'] = True
            corrected['currency_flagged_from'] = target_currency
            target_currency = detected_currency
            corrected['needs_review'] = True
            corrected.setdefault('issues', []).append(
                f"Currency detected as {detected_currency}, but user selected {corrected.get('currency', target_currency)}. Using detected currency.")
        # Store all values in native currency, but convert if requested
        if corrected['currency'] != target_currency:
            for item in corrected['items']:
                item['unit_price'] = self.currency.convert(item['unit_price'], corrected['currency'], target_currency)
            corrected['subtotal'] = self.currency.convert(corrected['subtotal'], corrected['currency'], target_currency)
            corrected['tax'] = self.currency.convert(corrected['tax'], corrected['currency'], target_currency)
            corrected['total'] = self.currency.convert(corrected['total'], corrected['currency'], target_currency)
            corrected['currency'] = target_currency
        # AI-generated category and notes
        notes_result = self.notes.generate(corrected, full_text)
        # Ensure extracted category matches available options
        category = notes_result.get('category') or corrected.get('category') or 'Other'
        if category not in TRANSACTION_CATEGORIES:
            category = 'Other'
        corrected['category'] = category
        corrected['note'] = notes_result.get('note', '')
        confirmed = self.confirmation.present(corrected)
        if confirmed.get('approved'):
            self.report.generate(confirmed)
        return confirmed

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <receipt_image_path> [target_currency]")
        sys.exit(1)
    image_path = sys.argv[1]
    target_currency = sys.argv[2] if len(sys.argv) > 2 else 'JPY'
    orchestrator = Orchestrator()
    orchestrator.process_receipt(image_path, target_currency)
