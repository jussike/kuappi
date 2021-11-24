import logging

from config import CONFIG
from abstract import AbstractSwitch

if 'KuappiGPIO' in CONFIG.get('controls'):
    from gpiozero import LED as GPIO


class KuappiGPIO(AbstractSwitch):
    def __init__(self):
        self.pin = CONFIG.get('gpio_pin')
        self.gpio = GPIO(self.pin)
        self.gpio.on()
        self._state = True

    def on(self):
        try:
            self.gpio.on()
            self._state = True
        except Exception:
            logging.exception('GPIO error when setting True')

    def off(self):
        try:
            self.gpio.off()
            self._state = False
        except Exception:
            logging.exception('GPIO error when setting False')

    def cleanup(self):
        pass

    @property
    def state(self):
        return self.gpio.value and self._state
