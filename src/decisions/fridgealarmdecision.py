from abstract import AbstractDecision
from common import TEMP

class FridgeAlarmDecision(AbstractDecision):
    hi_limit = 10
    low_limit = 0

    def get_decision(self, data, output_state=None):
        if not data or TEMP not in data.keys():
            return None
        temp = data[TEMP]
        return temp > self.hi_limit or temp < self.low_limit
