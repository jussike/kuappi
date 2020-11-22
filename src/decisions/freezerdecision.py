import logging

from abstract import AbstractDecision
from common import TEMP


class FreezerDecision(AbstractDecision):
    hard_hi_limit = -15
    hard_low_limit = -24

    def __init__(self):
        logging.info('Using FreezerDecision')

    def get_decision(self, data, output_state=None):
        temp = data[TEMP]
        if temp > self.hard_hi_limit:
            if output_state:
                return None
            return 1
        elif temp < self.hard_low_limit:
            if output_state:
                return None
            return 1
        return 0
