import logging

from abstract import AbstractSensor, AbstractDecision
from config import CONFIG


if 'MiTemp' == CONFIG.get('sensor'):
    from mitemp_bt.mitemp_bt_poller import MiTempBtPoller
    from btlewrap.bluepy import BluepyBackend


class MiTemp(AbstractSensor):
    def __init__(self):
        self.poller = MiTempBtPoller('58:2D:34:34:4C:3E', BluepyBackend, cache_timeout=300, retries=10)

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
    hum_full_limit = 70
    hum_med_limit = 50
    hum_low_limit = 35

    def get_decision(self, value, output_state=None):
        temp, hum = value
        decision = False
        if hum >= self.hum_full_limit:
            logging.info('Humidity %s, setting 8', hum)
            return 8
        elif hum >= self.hum_med_limit:
            logging.info('Humidity %s, setting 6', hum)
            return 6
        elif hum >= self.hum_low_limit:
            logging.info('Humidity %s, setting 5', hum)
            return 5
        else:
            logging.info('Humidity %s, setting 4', hum)
            return 4

