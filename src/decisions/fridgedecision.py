from abstract import AbstractDecision
from common import TEMP

class FridgeDecision(AbstractDecision):
    soft_hi_limit = 3.5
    soft_low_limit = 2.5
    hard_hi_limit = 7
    hard_low_limit = 0

    def get_decision(self, data, output_state=None):
        temp = data[TEMP]
        if temp > self.hard_hi_limit:
            return True
        elif temp < self.hard_low_limit:
            return False
        elif output_state is None:
            return None
        elif temp >= self.soft_hi_limit and not output_state:
            return True
        elif temp <= self.soft_low_limit and output_state:
            return False
        return None
