import unittest

from common import TEMP
from decisions.fridgedecision import FridgeDecision

class TestFridgeDecision(unittest.TestCase):

    def setUp(self):
        self.dec = FridgeDecision()

    def test_temp_below_hard_limit(self):
        temp = {TEMP: -1}
        decision = self.dec.get_decision(temp)
        self.assertEqual(decision, False)
        decision = self.dec.get_decision(temp, True)
        self.assertEqual(decision, False)
        decision = self.dec.get_decision(temp, False)
        self.assertEqual(decision, False)
        decision = self.dec.get_decision(temp, None)
        self.assertEqual(decision, False)

    def test_temp_below_soft_limit(self):
        temp = {TEMP: 1}
        decision = self.dec.get_decision(temp)
        self.assertEqual(decision, None)
        decision = self.dec.get_decision(temp, True)
        self.assertEqual(decision, False)
        decision = self.dec.get_decision(temp, False)
        self.assertEqual(decision, None)
        decision = self.dec.get_decision(temp, None)
        self.assertEqual(decision, None)

    def test_temp_between_limits(self):
        temp = {TEMP: 4}
        decision = self.dec.get_decision(temp)
        self.assertEqual(decision, None)
        decision = self.dec.get_decision(temp, True)
        self.assertEqual(decision, None)
        decision = self.dec.get_decision(temp, False)
        self.assertEqual(decision, None)
        decision = self.dec.get_decision(temp, None)
        self.assertEqual(decision, None)

    def test_temp_over_soft_limit(self):
        temp = {TEMP: 6}
        decision = self.dec.get_decision(temp)
        self.assertEqual(decision, None)
        decision = self.dec.get_decision(temp, True)
        self.assertEqual(decision, None)
        decision = self.dec.get_decision(temp, False)
        self.assertEqual(decision, True)
        decision = self.dec.get_decision(temp, None)
        self.assertEqual(decision, None)

    def test_temp_over_hard_limit(self):
        temp = {TEMP: 10}
        decision = self.dec.get_decision(temp)
        self.assertEqual(decision, True)
        decision = self.dec.get_decision(temp, True)
        self.assertEqual(decision, True)
        decision = self.dec.get_decision(temp, False)
        self.assertEqual(decision, True)
        decision = self.dec.get_decision(temp, None)
        self.assertEqual(decision, True)