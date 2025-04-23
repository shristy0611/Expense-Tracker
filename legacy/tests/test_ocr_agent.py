import unittest
from agents.ocr_agent import AgentOCR
import os

class TestAgentOCR(unittest.TestCase):
    def test_process(self):
        agent = AgentOCR()
        # Use a sample image path that exists for your test
        sample_image = os.path.join(os.path.dirname(__file__), '../sample_receipt.jpg')
        if not os.path.exists(sample_image):
            self.skipTest('Sample receipt image not found.')
        result = agent.process(sample_image)
        self.assertIn('segments', result)
        self.assertIsInstance(result['segments'], list)
        self.assertIn('flagged_for_review', result)

if __name__ == '__main__':
    unittest.main()
