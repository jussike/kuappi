import logging
import serial
import time
import threading

from abstract import AbstractControl
from valloxserial import vallox_serial


class ValloxControl(AbstractControl):
    def __init__(self):
        self.serial = vallox_serial
        self.serial.control = self
        self._speed = None

    @property
    def state(self):
        return self._speed

    @state.setter
    def state(self, state):
        self._speed = state

    def control(self, speed):
        if speed != self._speed:
            if speed > 0:
                self.serial.set_speed(speed)
            else:
                self.serial.power_off()

    def cleanup(self):
        pass
