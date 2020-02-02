import logging
import pywemo

from abstract import AbstractSwitch


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
