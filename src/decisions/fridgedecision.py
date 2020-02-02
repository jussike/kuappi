from abstract import AbstractDecision


class FridgeDecision(AbstractDecision):
    soft_hi_limit = 4.8
    soft_low_limit = 3.3
    hard_hi_limit = 7
    hard_low_limit = 0

    def get_decision(self, temp, output_state=None):
        if temp >= self.soft_hi_limit and output_state is False:
            return True
        elif temp <= self.soft_low_limit and output_state is True:
            return False
        elif temp > self.hard_hi_limit:
            return True
        elif temp < self.hard_low_limit:
            return False
        return None
