from abstract import AbstractDecision
from common import TEMP

class FridgeDecision(AbstractDecision):
    soft_hi_limit = 3.5
    soft_low_limit = 2.5
    hard_hi_limit = 7
    hard_low_limit = 0

    def __init__(self):
        super().__init__(zmq=True)
        self.temp = None

    def get_decision(self, data, output_state=None):
        self.temp = data[TEMP]
        if self.temp > self.hard_hi_limit:
            return True
        elif self.temp < self.hard_low_limit:
            return False
        elif output_state is None:
            return None
        elif self.temp >= self.soft_hi_limit and not output_state:
            return True
        elif self.temp <= self.soft_low_limit and output_state:
            return False
        return None

    def remote_ask_fridge_temp(self, **kwargs):
        if self.temp:
            self.zmq_pub.send('Fridge temperature is {}\u00b0C'.format(self.temp))
        else:
            self.zmq_pub.send('Fridge has no temp data')
