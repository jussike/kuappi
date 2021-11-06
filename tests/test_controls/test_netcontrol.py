import logging
from unittest import TestCase
from unittest.mock import patch
from controls.netcontrol import NetControl
from sensors.netsensor import NetSensor
from config import CONFIG

def setup_logging(log_file=None):
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=log_file,
                        format=log_format,
                        level=logging.DEBUG)
    logging.info('Logging is set')

class TestNetControl(TestCase):

    def setUp(self):
        setup_logging()
        CONFIG.update(
            {'netctl_host': '127.0.0.1'}
        )
        self.control = NetControl()
        self.sensor = NetSensor()

    def tearDown(self):
        self.control.cleanup()
        self.sensor.cleanup()

    def test_control(self):
        test_data = \
            b"{'battery': 25, 'voltage': 2785, 'temperature': 20.68, 'humidity': 75.62, 'pressure': 1987.2, 'linkquality': 139}"
        self.control.control(test_data)

        data = None
        while not data:
            data = self.sensor.get_data()
        self.assertEqual(data, test_data)
