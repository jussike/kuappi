from unittest import TestCase
from unittest.mock import patch
with patch('serial.Serial'):
    from controls.valloxcontrol import ValloxControl
from valloxserial import vallox_serial


class TestValloxControl(TestCase):

    @patch('serial.Serial')
    def setUp(self, _):
        self.vc = ValloxControl()

    @patch.object(vallox_serial, 'set_speed')
    def test_control_same_speed(self, set_speed):
        self.vc.state = 1
        self.vc.control(1)
        self.assertFalse(set_speed.called)

    @patch.object(vallox_serial, 'set_speed')
    def test_control_change_speed(self, set_speed):
        self.vc.state = 1
        self.vc.control(2)
        set_speed.assert_called_with(2)

    def test_control_data(self):
        data = self.vc.serial.get_control_data('host', 'speed', 2)
        expected = b'\x01\x22\x11\x29\x03'
        checksum = 0
        for byte in expected:
            checksum += byte
            checksum = checksum & 0xff
        expected += bytes((checksum,))
        self.assertEqual(expected, data)
