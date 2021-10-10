import logging

from abstract import AbstractDecision
from common import TEMP


class FreezerDecision(AbstractDecision):
    hard_hi_limit = -13
    hard_low_limit = -24
    cached_limit = 90
    warn_limit = 10

    def __init__(self):
        logging.info('Using FreezerDecision')
        self.cached_data_count = 0
        self.old_data = None

    def get_decision(self, data, output_state=None):
        if data == self.old_data:
            self.cached_data_count += 1
            if self.cached_data_count >= self.cached_limit:
                logging.error('Data has been same %d times, raising alarm', self.cached_data_count)
                return True
            elif self.cached_data_count >= self.warn_limit:
                logging.info('Data has been same than previous one %d times. There may be problem with the data source', self.cached_data_count)
        else:
            self.cached_data_count = 0
            self.old_data = data

        if self.hard_low_limit <= data[TEMP] <= self.hard_hi_limit:
            return False
        return True
