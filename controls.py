import logging

from config import CONFIG
from abstract import AbstractSwitch, AbstractControl

if 'Wemo' in CONFIG.get('controls'):
    import pywemo
if 'KuappiGPIO' in CONFIG.get('controls'):
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
        self._state = True

    def on(self):
        try:
            GPIO.output(self.pin, True)
            self._state = True
        except:
            logging.error('GPIO error when setting True')

    def off(self):
        try:
            GPIO.output(self.pin, False)
            self._state = False
        except:
            logging.error('GPIO error when setting False')

    def cleanup(self):
        GPIO.cleanup(self.pin)

    @property
    def state(self):
        return GPIO.input(self.pin) and self._state is True


class OutputControl(AbstractControl, AbstractSwitch):
    def __init__(self, outputs=None):
        self.outputs = outputs

    def set_outputs(self, outputs):
        self.outputs = outputs

    def on(self):
        for output in self.outputs:
            if isinstance(output, AbstractSwitch):
                output.on()
            else:
                logging.error('%s is not instance of AbstractSwitch', output)

    def off(self):
        for output in self.outputs:
            if isinstance(output, AbstractSwitch):
                output.off()
            else:
                logging.error('%s is not instance of AbstractSwitch', output)

    def cleanup(self):
        for output in self.outputs:
            if isinstance(output, AbstractSwitch):
                output.cleanup()
            # Other types of outputs don't need this cleanup

    @property
    def state(self):
        return all(v.state for v in self.outputs)

    def control(self, param):
        if param is True:
            self.on()
        elif param is False:
            self.off()
        elif isinstance(param, int):
            for output in self.outputs:
                if isinstance(output, AbstractControl):
                    output.control(param)
                else:
                    logging.error('%s is not instance of AbstractControl', output)
