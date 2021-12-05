import logging

from abstract import AbstractDecision
from common import HUM, TEMP
from config import CONFIG
from valloxserial import vallox_serial
from valloxntc import get_vallox_temp


class ValloxDecision(AbstractDecision):
    hum_8_limit = 92
    hum_7_limit = 80
    hum_6_limit = 65
    hum_5_limit = 60
    speed_max = 8
    speed_normal_min = 4
    speed_too_hot = 2
    limit_inside = 25

    def __init__(self):
        super().__init__(zmq=True)
        self.vallox = vallox_serial
        self._summer_speed_control = None

    def summer_speed_control(self, data):
        raw = self.vallox.ask_vallox('intake_temp')
        if not raw:
            logging.error("vallox didn't answer intake_temp")
            return self._summer_speed_control
        temp = get_vallox_temp(raw)
        if data[TEMP] <= self.limit_inside:
            # Use humidity based control
            logging.info('Using humidity based control')
            self._summer_speed_control = None
            return self._summer_speed_control

        # Force speed to high or low
        logging.info('vallox intake temp %d, sensor temp %.1f', temp, data[TEMP])
        self._summer_speed_control = temp < (data[TEMP] - 1)
        return self._summer_speed_control

    def get_decision(self, data, _=None):
        if self.remote_controlled:
            logging.debug('Remote controlled to %d', self.remote_control_decision)
            self.zmq_pub.send_alarm('Remote controlled to {} for {} secs'.format(self.remote_control_decision, self.control_time))
            return self.remote_control_decision
        else:
            self.zmq_pub.normal()

        if CONFIG.get('summer_mode'):
            summer_speed_control = self.summer_speed_control(data)
            if summer_speed_control is None:
                return self.humidity_decision(data)
            elif summer_speed_control:
                logging.info('Cold outside, maximizing speed: %d', self.speed_max)
                return self.speed_max
            elif self.humidity_decision(data) == self.speed_normal_min:
                logging.info('Hot outside, minimizing speed: %d', self.speed_too_hot)
                return self.speed_too_hot
        return self.humidity_decision(data)

    def humidity_decision(self, data):
        hum = data[HUM]
        if hum >= self.hum_8_limit:
            logging.info('Humidity %s, setting %d', hum, self.speed_max)
            return self.speed_max
        elif hum >= self.hum_7_limit:
            logging.info('Humidity %s, setting 7', hum)
            return 7
        elif hum >= self.hum_6_limit:
            logging.info('Humidity %s, setting 6', hum)
            return 6
        elif hum >= self.hum_5_limit:
            logging.info('Humidity %s, setting 5', hum)
            return 5
        else:
            logging.debug('Humidity %s, setting %d', hum, self.speed_normal_min)
            return self.speed_normal_min

    def remote_speed(self, **kwargs):
        cmd_speed = kwargs['speed'] if kwargs and 'speed' in kwargs else None
        cmd_time = kwargs['time'] if kwargs and 'time' in kwargs else None
        if cmd_speed is not None:
            logging.info('Controlling with cmd speed %d and time %d', cmd_speed, cmd_time)
            self.control(decision=cmd_speed, control_time=cmd_time)
        else:
            speed = self.vallox.ask_vallox('speed')
            if speed is None:
                self.zmq_pub.send("Speed: Vallox didn't response any valid value")
                return
            speed = self.vallox.vallox_speed_value_to_number(speed)
            logging.info('Vallox told that speed is {}'.format(speed))
            self.zmq_pub.send('Vallox told that speed is {}'.format(speed))
