import unittest

from decisions.valloxdecision import ValloxDecision

class TestValloxDecision(unittest.TestCase):

    def setUp(self):
        self.vdec = ValloxDecision()

    def test_hum_100(self):
        decision = self.vdec.get_decision((0,100))
        self.assertEqual(decision, 8)

    def test_hum_80(self):
        decision = self.vdec.get_decision((0,80))
        self.assertEqual(decision, 7)

    def test_hum_50(self):
        decision = self.vdec.get_decision((0,50))
        self.assertEqual(decision, 5)

    def test_hum_0(self):
        decision = self.vdec.get_decision((0,0))
        self.assertEqual(decision, 4)
