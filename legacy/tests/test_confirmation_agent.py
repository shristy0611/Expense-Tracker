import unittest
from agents.confirmation_agent import AgentConfirmation

class TestAgentConfirmation(unittest.TestCase):
    def test_present(self):
        agent = AgentConfirmation()
        transaction = {'vendor': 'LAWSON', 'total': 606}
        confirmed = agent.present(transaction)
        self.assertTrue(confirmed['approved'])

if __name__ == '__main__':
    unittest.main()
