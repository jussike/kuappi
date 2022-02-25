import logging

from abstract import AbstractDecision
from common import HUM, TEMP
from config import CONFIG
from subprocess import Popen, DEVNULL
from valloxserial import vallox_serial
from valloxntc import get_vallox_temp
import time


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
        self._online_devices_count = 0
        self._online_devices_timestamp = None
        self._online_devices = CONFIG.get('online_devices', ("192.168.1.110", "192.168.1.111"))
        self._ping_interval = CONFIG.get('ping_interval', 600)

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
        return self.humidity_decision(data) - self.online_devices_reduction()

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
            if cmd_time is not None:
                logging.info('Controlling with cmd speed %d and time %d', cmd_speed, cmd_time)
                self.control(decision=cmd_speed, control_time=cmd_time)
            else:
                cb = lambda: self.zmq_pub.send('Vallox speed is {}'.format(cmd_speed))
                self.vallox.set_speed(cmd_speed, update_state=False, callback=cb)
        else:
            select = self.vallox.ask_vallox('select')
            if select is None:
                self.zmq_pub.send("Speed: Vallox didn't response any valid value")
                return

            if not select & 1:
                self.zmq_pub.send("Speed: Vallox is off")
                return

            speed = self.vallox.ask_vallox('speed')
            if speed is None:
                self.zmq_pub.send("Speed: Vallox didn't response any valid value but its power is on")
                return
            speed = self.vallox.vallox_speed_value_to_number(speed)
            logging.info('Vallox speed is {}'.format(speed))
            if self.remote_controlled:
                self.zmq_pub.send('Vallox speed is {}, remote controlled to {}, {:.0f} secs remaining'.format(speed, self.remote_control_decision, self.remote_controlled))
            else:
                self.zmq_pub.send('Vallox speed is {}'.format(speed))

    def remote_air_heating(self, **kwargs):
        heating_bit = 0x8
        cmd_setting = kwargs['setting'] if kwargs and 'setting' in kwargs else None
        select = self.vallox.ask_vallox('select')
        if cmd_setting is None:
            if select & heating_bit:
                self.zmq_pub.send('Heating is on')
            else:
                self.zmq_pub.send('Heating is off')
            return
        if cmd_setting:
            cb = lambda: self.zmq_pub.send('Heating is on')
        else:
            cb = lambda: self.zmq_pub.send('Heating is off')
        self.vallox.set_heating(cmd_setting, select, callback=cb)

    def online_devices_reduction(self):
        online = self.online_devices()
        if online == 0:
            return 2
        elif online == 1:
            return 1
        else:
            return 0

    def online_devices(self):
        if self._online_devices_timestamp and \
            self._online_devices_timestamp + self._ping_interval > time.monotonic():
            return self._online_devices_count

        self._online_devices_count = 0
        PACKET_LOSS_MAX = 3

        for device in self._online_devices:
            packet_loss = 0
            while packet_loss < PACKET_LOSS_MAX:
                self.proc = Popen(
                    ("ping", "-c1", "-q", "-W1", device),
                    stdout=DEVNULL,
                    stderr=DEVNULL,
                )
                self.proc.wait()
                if not self.proc.returncode:
                    self._online_devices_count += 1
                    break
                else:
                    packet_loss += 1

        self._online_devices_timestamp = time.monotonic()

        return self._online_devices_count
