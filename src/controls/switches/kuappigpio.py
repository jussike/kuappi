import logging

from config import CONFIG
from abstract import AbstractSwitch

if 'KuappiGPIO' in CONFIG.get('controls'):
    import RPi.GPIO as GPIO


class KuappiGPIO(AbstractSwitch):
    def __init__(self):
        self.pin = CONFIG.get('gpio_pin')
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.HIGH)
        self._state = True

    def on(self):
        try:
            GPIO.output(self.pin, True)
            self._state = True
        except Exception:
            logging.exception('GPIO error when setting True')

    def off(self):
        try:
            GPIO.output(self.pin, False)
            self._state = False
        except Exception:
            logging.exception('GPIO error when setting False')

    def cleanup(self):
        GPIO.cleanup(self.pin)

    @property
    def state(self):
        return GPIO.input(self.pin) and self._state
