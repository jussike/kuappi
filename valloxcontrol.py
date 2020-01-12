import logging

from config import CONFIG
from abstract import AbstractSwitch, AbstractControl

class ValloxControl(AbstractControl):
    @property
    def state(self):
        return None
    def control(self, param):
        pass

