import logging

from abstract import AbstractDecision
from common import TEMP

class FridgeAlarmDecision(AbstractDecision):
    hi_limit = 10
    low_limit = 0
    cached_limit = 50
    warn_limit = 10

    def __init__(self):
        super().__init__(zmq=True)
        logging.info('Using FridgeAlarmDecision')
        self.cached_data_count = 0
        self.old_data = None

    def get_decision(self, data, output_state=None):
        if self.remote_controlled:
            logging.info('Snoozed')
            if not self.remote_control_decision:
                self.zmq_pub.normal()
            return self.remote_control_decision

        if data == self.old_data:
            self.cached_data_count += 1
            if self.cached_data_count >= self.cached_limit:
                logging.error('Data may be too old, raising alarm')
                self.zmq_pub.send_alarm('Alarm: Old data!')
                return True
            elif self.cached_data_count >= self.warn_limit:
                logging.info('Data has been same than previous one %d times. There may be problem with the data source', self.cached_data_count)
        else:
            self.cached_data_count = 0
            self.old_data = data

        if not data or TEMP not in data.keys():
            return None

        if data[TEMP] > self.hi_limit or data[TEMP] < self.low_limit:
            self.zmq_pub.send_alarm('Alarm: Temperature {} is outside of the limits ({} - {})'.format(data[TEMP], self.low_limit, self.hi_limit))
            return True

        self.zmq_pub.normal()
        return False

    def remote_snooze(self, **kwargs):
        self.control()
        self.zmq_pub.send('Snoozed for {} secs'.format(self.control_time))

    def remote_ask_temp(self, **kwargs):
        if self.old_data and TEMP in self.old_data:
            self.zmq_pub.send('Fridge temperature is {}\u00b0C'.format(self.old_data[TEMP]))
        else:
            self.zmq_pub.send("Sensor didn't send temp yet")
