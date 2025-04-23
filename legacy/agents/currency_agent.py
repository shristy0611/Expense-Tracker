import requests
from datetime import datetime

class AgentCurrency:
    def __init__(self):
        self.cache = {}  # {('USD', 'JPY', '2025-04-21'): rate}

    def get_rate(self, from_cur, to_cur, date=None):
        date = date or datetime.today().strftime('%Y-%m-%d')
        key = (from_cur, to_cur, date)
        if key in self.cache:
            return self.cache[key]
        # Placeholder: replace with actual API call
        rate = 1.0 if from_cur == to_cur else 0.007  # Example: 1 JPY = 0.007 USD
        self.cache[key] = rate
        return rate

    def convert(self, amount, from_cur, to_cur, date=None):
        rate = self.get_rate(from_cur, to_cur, date)
        return amount * rate
