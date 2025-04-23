import unittest
from agents.categorizer_agent import AgentCategorizer

class TestAgentCategorizer(unittest.TestCase):
    def test_parse(self):
        agent = AgentCategorizer()
        ocr_json = {
            'segments': [
                {'text': 'LAWSON', 'confidence': 95},
                {'text': '2020/01/22', 'confidence': 90},
                {'text': '合計 ¥606', 'confidence': 92},
                {'text': 'MACHIコーヒー(S) 1 ¥100', 'confidence': 93},
            ]
        }
        result = agent.parse(ocr_json)
        self.assertIn('vendor', result)
        self.assertIn('items', result)
        self.assertIsInstance(result['items'], list)
        self.assertIn('total', result)

if __name__ == '__main__':
    unittest.main()
