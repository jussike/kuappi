import logging

from abstract import AbstractSensor, AbstractControl
from config import CONFIG


if 'Mitemp' == CONFIG.get('sensor'):
    from mitemp_bt.mitemp_bt_poller import MiTempBtPoller
    from btlewrap.bluepy import BluepyBackend


class MiTemp(AbstractSensor):
    def __init__(self):
        self.poller = MiTempBtPoller('58:2D:34:34:4C:3E', BluepyBackend)

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


class MiTempControl(AbstractControl):

    def get_decision(self, temp, output_state=None):
        return None
