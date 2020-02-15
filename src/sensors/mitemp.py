import logging

from abstract import AbstractSensor
from config import CONFIG

from mitemp_bt.mitemp_bt_poller import MiTempBtPoller
from btlewrap.bluepy import BluepyBackend


class MiTemp(AbstractSensor):
    def __init__(self):
        cache_timeout = CONFIG.get('mitemp_cache_timeout', 300)
        self.poller = MiTempBtPoller(CONFIG.get('mitemp_addr'), BluepyBackend, cache_timeout=cache_timeout, retries=10)

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
