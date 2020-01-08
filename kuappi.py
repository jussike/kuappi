from abc import ABCMeta, abstractmethod, abstractproperty
import glob
import logging
import os
import time

import redis

try:
    import pywemo
    wemo_imported = True
except:
    wemo_imported = False

try:
    import RPi.GPIO as GPIO
    rpi_gpio_imported = True
except:
    rpi_gpio_imported = False


current_millis = lambda: int(round(time.time() * 1000))


def setup_logging(log_file=None):
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    logging.basicConfig(filename=log_file,
                        format=log_format,
                        level=logging.DEBUG)


class AbstractSensor(metaclass=ABCMeta):
    @abstractmethod
    def get_value():
        pass


class Temp(AbstractSensor):
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

    def get_value(self):
        return self.read_temp()


class AbstractControl(metaclass=ABCMeta):
    @abstractmethod
    def get_decision(self, value, state=None):
        pass


class TempControl(AbstractControl):
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

    def add_multi(self, values, keys=('temp', 'switch')):
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


class OutputControl:
    def __init__(self, outputs=None):
        self.outputs = outputs
    def set_outputs(self, outputs):
        self.outputs = outputs
    def on(self):
        for output in self.outputs:
            output.on()
    def off(self):
        for output in self.outputs:
            output.off()
    @property
    def state(self):
        return all(v.state for v in self.outputs)


class KuappiGPIO:
    def __init__(self):
        self.pin = 17
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


def create_instance(sensor_class):
    return sensor_class()


def main():
    setup_logging('/tmp/log')
    redis = Redis()
    outputs = []
    if wemo_imported:
        outputs.append(Wemo())
    if rpi_gpio_imported:
        outputs.append(KuappiGPIO())
    output = OutputControl()
    output.set_outputs(outputs)
    sensor = create_instance(Temp)
    control = create_instance(TempControl)

    while True:
        try:
            value = sensor.get_value()
            if control.get_decision(value, output.state) is True:
                output.on()
            elif control.get_decision(value, output.state) is False:
                output.off()
            logging.debug('%s %s' % (value, output.state))
            redis.add_multi((value, 1 if output.state else 0))
            time.sleep(30)
        except KeyboardInterrupt:
            logging.info("stopping")
            break


main()
GPIO.cleanup(channel)
