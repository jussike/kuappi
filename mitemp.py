import logging

from abstract import AbstractSensor, AbstractDecision
from config import CONFIG

from mitemp_bt.mitemp_bt_poller import MiTempBtPoller
from btlewrap.bluepy import BluepyBackend


class MiTemp(AbstractSensor):
    def __init__(self):
        cache_timeout = CONFIG.get('mitemp_cache_timeout', 300)
        self.poller = MiTempBtPoller('58:2D:34:34:4C:3E', BluepyBackend, cache_timeout=cache_timeout, retries=10)

    def read_values(self):
        temp = None
        hum = None
        while temp is None or hum is None:
            try:
                temp = self.poller.parameter_value("temperature")
                hum = self.poller.parameter_value("humidity")
            except:
                logging.exception('Failed to read temp')
        return (temp, hum)

    def get_value(self):
        return self.read_values()


class MiTempControl(AbstractDecision):
    hum_8_limit = 92
    hum_7_limit = 80
    hum_6_limit = 60
    hum_5_limit = 35

    def get_decision(self, value, output_state=None):
        temp, hum = value
        decision = False
        if hum >= self.hum_8_limit:
            logging.info('Humidity %s, setting 8', hum)
            return 8
        elif hum >= self.hum_7_limit:
            logging.info('Humidity %s, setting 7', hum)
            return 7
        elif hum >= self.hum_6_limit:
            logging.info('Humidity %s, setting 6', hum)
            return 6
        elif hum >= self.hum_5_limit:
            logging.info('Humidity %s, setting 5', hum)
            return 5
        else:
            logging.info('Humidity %s, setting 4', hum)
            return 4

