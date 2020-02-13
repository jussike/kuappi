import unittest

from decisions.fridgedecision import FridgeDecision

class TestFridgeDecision(unittest.TestCase):

    def setUp(self):
        self.dec = FridgeDecision()

    def test_temp_below_hard_limit(self):
        decision = self.dec.get_decision(-1)
        self.assertEqual(decision, False)
        decision = self.dec.get_decision(-1, True)
        self.assertEqual(decision, False)
        decision = self.dec.get_decision(-1, False)
        self.assertEqual(decision, False)
        decision = self.dec.get_decision(-1, None)
        self.assertEqual(decision, False)

    def test_temp_below_soft_limit(self):
        decision = self.dec.get_decision(1)
        self.assertEqual(decision, None)
        decision = self.dec.get_decision(1, True)
        self.assertEqual(decision, False)
        decision = self.dec.get_decision(1, False)
        self.assertEqual(decision, None)
        decision = self.dec.get_decision(1, None)
        self.assertEqual(decision, None)

    def test_temp_between_limits(self):
        decision = self.dec.get_decision(4)
        self.assertEqual(decision, None)
        decision = self.dec.get_decision(4, True)
        self.assertEqual(decision, None)
        decision = self.dec.get_decision(4, False)
        self.assertEqual(decision, None)
        decision = self.dec.get_decision(4, None)
        self.assertEqual(decision, None)

    def test_temp_over_soft_limit(self):
        decision = self.dec.get_decision(6)
        self.assertEqual(decision, None)
        decision = self.dec.get_decision(6, True)
        self.assertEqual(decision, None)
        decision = self.dec.get_decision(6, False)
        self.assertEqual(decision, True)
        decision = self.dec.get_decision(6, None)
        self.assertEqual(decision, None)

    def test_temp_over_hard_limit(self):
        decision = self.dec.get_decision(10)
        self.assertEqual(decision, True)
        decision = self.dec.get_decision(10, True)
        self.assertEqual(decision, True)
        decision = self.dec.get_decision(10, False)
        self.assertEqual(decision, True)
        decision = self.dec.get_decision(10, None)
        self.assertEqual(decision, True)