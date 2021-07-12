import logging

from abstract import AbstractDecision
from common import HUM, TEMP
from config import CONFIG
from valloxserial import vallox_serial
from valloxntc import get_vallox_temp


class ValloxDecision(AbstractDecision):
    hum_8_limit = 92
    hum_7_limit = 80
    hum_6_limit = 60
    hum_5_limit = 45
    speed_max = 8
    speed_normal_min = 4
    speed_too_hot = 2

    def __init__(self):
        self.vallox = vallox_serial

    def is_cold(self, data):
        raw = self.vallox.ask_vallox('intake_temp')
        if not raw:
            return False
        temp = get_vallox_temp(raw)
        return temp < data[TEMP]

    def get_decision(self, data, _=None):
        if CONFIG.get('summer_mode'):
            if self.is_cold(data):
                logging.info('Cold outside, maximizing speed: %d', self.speed_max)
                return self.speed_max
            elif self.humidity_decision(data) == self.speed_normal_min:
                logging.info('Hot outside, minimizing speed: %d', self.speed_too_hot)
                return self.speed_too_hot
        return self.humidity_decision(data)

    def humidity_decision(self, data):
        hum = data[HUM]
        if hum >= self.hum_8_limit:
            logging.info('Humidity %s, setting %d', hum, self.speed_max)
            return self.speed_max
        elif hum >= self.hum_7_limit:
            logging.info('Humidity %s, setting 7', hum)
            return 7
        elif hum >= self.hum_6_limit:
            logging.info('Humidity %s, setting 6', hum)
            return 6
        elif hum >= self.hum_5_limit:
            logging.info('Humidity %s, setting 5', hum)
            return 5
        else:
            logging.info('Humidity %s, setting %d', hum, self.speed_normal_min)
            return self.speed_normal_min
