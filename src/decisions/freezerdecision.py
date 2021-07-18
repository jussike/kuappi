import logging

from abstract import AbstractDecision
from common import TEMP, QUALITY


class FreezerDecision(AbstractDecision):
    hard_hi_limit = -13
    hard_low_limit = -24
    error_limit = 50

    def __init__(self):
        logging.info('Using FreezerDecision')
        self.errors = 0

    def get_decision(self, data, output_state=None):
        temp = data[TEMP]
        quality = data[QUALITY]

        if quality:
            self.errors = 0
        else:
            self.errors += 1
            logging.info('Very bad link quality, raising error counter')
            if self.errors >= self.error_limit:
                logging.error('No link, starting alarm')
                return 1

        if temp > self.hard_hi_limit:
            return 1
        elif temp < self.hard_low_limit:
            return 1
        return 0
