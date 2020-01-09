import logging

from config import CONFIG
from abstract import AbstractSwitch

if 'pywemo' in CONFIG.get('controls'):
    import pywemo
if 'rpi_gpio' in CONFIG.get('controls'):
    import RPi.GPIO as GPIO


class Wemo(AbstractSwitch):
    def __init__(self):
        wemo = pywemo.discover_devices()
        self.wemo = wemo[0] # Crash if device not found
        self.on()

    def on(self):
        try:
            self.wemo.on()
            self.state = True
        except:
            logging.error('wemo error (on)')

    def off(self):
        try:
            self.wemo.off()
            self.state = False
        except:
            logging.error('wemo error (off)')

    def cleanup(self):
        pass


class KuappiGPIO(AbstractSwitch):
    def __init__(self):
        self.pin = 17
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.HIGH)
        self.state = True

    def on(self):
        try:
            GPIO.output(self.pin, True)
            self.state = True
        except:
            logging.error('GPIO error when setting True')

    def off(self):
        try:
            GPIO.output(self.pin, False)
            self.state = False
        except:
            logging.error('GPIO error when setting False')

    def cleanup(self):
        GPIO.cleanup(self.pin)


class OutputControl(AbstractSwitch):
    def __init__(self, outputs=None):
        self.outputs = outputs

    def set_outputs(self, outputs):
        self.outputs = outputs

    def on(self):
        for output in self.outputs:
            output.on()

    def off(self):
        for output in self.outputs:
            output.off()

    def cleanup(self):
        for output in self.outputs:
            output.cleanup()

    @property
    def state(self):
        return all(v.state for v in self.outputs)
