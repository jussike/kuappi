import logging

from abstract import AbstractDecision

class ValloxDecision(AbstractDecision):
    hum_8_limit = 92
    hum_7_limit = 80
    hum_6_limit = 60
    hum_5_limit = 35

    def get_decision(self, value, _=None):
        temp, hum = value
        if hum >= self.hum_8_limit:
            logging.info('Humidity %s, setting 8', hum)
            return 8
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
            logging.info('Humidity %s, setting 4', hum)
            return 4

