import unittest

from common import TEMP, HUM
from decisions.valloxdecision import ValloxDecision

class TestValloxDecision(unittest.TestCase):

    def setUp(self):
        self.vdec = ValloxDecision()

    def test_hum_100(self):
        data = {TEMP: 0, HUM: 100}
        decision = self.vdec.get_decision(data)
        self.assertEqual(decision, 8)

    def test_hum_80(self):
        data = {TEMP: 0, HUM: 80}
        decision = self.vdec.get_decision(data)
        self.assertEqual(decision, 7)

    def test_hum_50(self):
        data = {TEMP: 0, HUM: 50}
        decision = self.vdec.get_decision(data)
        self.assertEqual(decision, 5)

    def test_hum_0(self):
        data = {TEMP: 0, HUM: 0}
        decision = self.vdec.get_decision(data)
        self.assertEqual(decision, 4)
