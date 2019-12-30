import glob
import time
import pywemo
import redis
import os
import logging

import RPi.GPIO as GPIO


def setup_logging(log_file=None):
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    logging.basicConfig(filename=log_file,
                        format=log_format,
                        level=logging.DEBUG)


current_millis = lambda: int(round(time.time() * 1000))

class Temp:
    soft_hi_limit = 4.8
    soft_low_limit = 3.3
    hard_hi_limit = 7
    hard_low_limit = 0

    def __init__(self):
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'

    def read_temp_raw(self):
        try:
            with open(self.device_file, 'r') as fh:
                return fh.readlines()
        except:
            logging.error('error reading raw data')
 
    def read_temp(self):
        lines = self.read_temp_raw()
        while lines is None or lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()

        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c


class Redis:
    def __init__(self):
        redis_host = "localhost"
        redis_port = 6379
        redis_password = ""
        try:
            self.redis = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
        except Exception as e:
            logging.exception(e)

    def add(self, value, key='temp'):
        c_time = current_millis()
        self.redis.zadd(key, {"%s:%s" % (c_time, value): c_time})

    def add_multi(self, values, keys=['temp', 'switch']):
        kv_dict = dict(zip(keys, values))
        c_time = current_millis()
        for key, value in kv_dict.items():
            self.redis.zadd(key, {"%s:%s" % (c_time, value): c_time})


class Wemo:
    def __init__(self):
        wemo = pywemo.discover_devices()
        self.wemo = wemo[0] # Crash if device not found
        self.on()

    def on(self):
        try:
            self.wemo.on()
            self.state = True
        except:
            logging.error('wemo error (on)')

    def off(self):
        try:
            self.wemo.off()
            self.state = False
        except:
            logging.error('wemo error (off)')


class Control:
    def __init__(self):
        self.controls = None
    def set_controls(self, controls):
        self.controls = controls
    def on(self):
        for control in self.controls:
            control.on()
    def off(self):
        for control in self.controls:
            control.off()
    @property
    def state(self):
        return all([v.state for v in self.controls])


class KuappiGPIO:
    def __init__(self):
        self.pin = 17
        #GPIO.setmode(GPIO.BOARD)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.HIGH)
        self.state = True

    def on(self):
        try:
            GPIO.output(self.pin, True)
            self.state = True
        except:
            logging.error('GPIO error when setting True')

    def off(self):
        try:
            GPIO.output(self.pin, False)
            self.state = False
        except:
            logging.error('GPIO error when setting False')

def main():
    setup_logging('/tmp/log')
    redis = Redis()
    temp = Temp()
    wemo = Wemo()
    gpio = KuappiGPIO()
    ctrl = Control()
    ctrl.set_controls((wemo, gpio))

    while True:
        try:
            _temp = temp.read_temp()
            if _temp >= temp.soft_hi_limit and ctrl.state is False:
                ctrl.on()
            elif _temp <= temp.soft_low_limit and ctrl.state is True:
                ctrl.off()
            elif _temp > temp.hard_hi_limit:
                ctrl.on()
            elif _temp < temp.hard_low_limit:
                ctrl.off()
            logging.debug('%s %s' % (_temp, ctrl.state))
            redis.add_multi([_temp, 1 if ctrl.state else 0])
            time.sleep(30)
        except KeyboardInterrupt:
            logging.info("stopping")
            break


main()
GPIO.cleanup(channel)
