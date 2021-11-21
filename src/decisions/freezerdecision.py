import logging

from abstract import AbstractDecision
from common import TEMP


class FreezerDecision(AbstractDecision):
    hard_hi_limit = -13
    hard_low_limit = -24
    cached_limit = 90
    warn_limit = 10

    def __init__(self):
        super().__init__(zmq=True)
        logging.info('Using FreezerDecision')
        self.zmq_pub.send('Initializing freezer')
        self.cached_data_count = 0
        self.old_data = None

    def get_decision(self, data, output_state=None):
        if self.remote_controlled:
            logging.info('Snoozed')
            if self.remote_control_decision:
                self.zmq_pub.send_alarm('Alarm via remote control!')
            else:
                self.zmq_pub.normal()
            return self.remote_control_decision
        if data == False:
            logging.error('False data received, raising alarm')
            self.zmq_pub.send_alarm('Alarm! False data received')
            return True
        if data == self.old_data:
            self.cached_data_count += 1
            if self.cached_data_count >= self.cached_limit:
                logging.error('Data has been same %d times, raising alarm', self.cached_data_count)
                self.zmq_pub.send_alarm('Alarm: Old data!')
                return True
            elif self.cached_data_count >= self.warn_limit:
                logging.info('Data has been same than previous one %d times. There may be problem with the data source', self.cached_data_count)
        else:
            self.cached_data_count = 0
            self.old_data = data

        if self.hard_low_limit <= data[TEMP] <= self.hard_hi_limit:
            self.zmq_pub.normal()
            return False

        self.zmq_pub.send_alarm('Alarm! Temperature {} is outside of the limits ({} - {})!'.format(data[TEMP], self.hard_low_limit, self.hard_hi_limit))
        return True

    def remote_snooze(self, **kwargs):
        self.control()
        self.zmq_pub.send('Snoozed for {} secs'.format(self.control_time))
