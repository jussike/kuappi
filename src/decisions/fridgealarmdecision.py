import logging

from abstract import AbstractDecision
from common import TEMP

class FridgeAlarmDecision(AbstractDecision):
    hi_limit = 10
    low_limit = 0
    cached_limit = 50
    warn_limit = 10

    def __init__(self):
        logging.info('Using FridgeAlarmDecision')
        self.cached_data_count = 0
        self.old_data = None

    def get_decision(self, data, output_state=None):
        if data == self.old_data:
            self.cached_data_count += 1
            if self.cached_data_count >= self.cached_limit:
                logging.error('Data may be too old, raising alarm')
                return True
            elif self.cached_data_count >= self.warn_limit:
                logging.info('Data has been same than previous one %d times. There may be problem with the data source', self.cached_data_count)
        else:
            self.cached_data_count = 0
            self.old_data = data

        if not data or TEMP not in data.keys():
            return None

        temp = data[TEMP]
        return temp > self.hi_limit or temp < self.low_limit
