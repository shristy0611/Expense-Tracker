import unittest
from agents.report_agent import AgentReport

class TestAgentReport(unittest.TestCase):
    def test_generate(self):
        agent = AgentReport()
        transaction = {'vendor': 'LAWSON', 'total': 606, 'approved': True}
        result = agent.generate(transaction)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
