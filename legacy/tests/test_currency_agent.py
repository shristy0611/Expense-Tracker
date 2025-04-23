import unittest
from agents.currency_agent import AgentCurrency

class TestAgentCurrency(unittest.TestCase):
    def test_conversion(self):
        agent = AgentCurrency()
        amount_jpy = 1000
        converted = agent.convert(amount_jpy, 'JPY', 'USD')
        self.assertIsInstance(converted, float)
        self.assertGreater(converted, 0)
        self.assertAlmostEqual(agent.convert(100, 'JPY', 'JPY'), 100)

if __name__ == '__main__':
    unittest.main()
