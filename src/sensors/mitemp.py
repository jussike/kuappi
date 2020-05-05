import logging

from abstract import AbstractSensor
from common import TEMP, HUM
from config import CONFIG

from mitemp_bt.mitemp_bt_poller import MiTempBtPoller
from btlewrap.bluepy import BluepyBackend


class MiTemp(AbstractSensor):
    def __init__(self):
        cache_timeout = CONFIG.get('mitemp_cache_timeout', 300)
        self.poller = MiTempBtPoller(CONFIG.get('mitemp_addr'), BluepyBackend, cache_timeout=cache_timeout, retries=10)

    def _read_data(self):
        temp = None
        hum = None
        while temp is None or hum is None:
            try:
                temp = self.poller.parameter_value(TEMP)
                hum = self.poller.parameter_value(HUM)
            except:
                logging.exception('Failed to read temp')
        return {TEMP: temp,
                HUM: hum}

    def get_data(self):
        return self._read_data()
