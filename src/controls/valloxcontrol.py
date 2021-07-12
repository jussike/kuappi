import logging
import serial
import time
import threading

from abstract import AbstractControl
from valloxserial import ValloxSerial


class ValloxControl(AbstractControl):
    def __init__(self):
        self.serial = ValloxSerial(self)
        self._speed = None

    @property
    def state(self):
        return self._speed

    @state.setter
    def state(self, state):
        self._speed = state

    def control(self, speed):
        if speed != self._speed:
            self.serial.set_speed(speed)
