import logging
from abstract import AbstractDecision


class PassthruDecision(AbstractDecision):
    def get_decision(self, data, output_state=None):
        if data is None:
            logging.info('Passthru: No data')
            return None
        return True if data else False
