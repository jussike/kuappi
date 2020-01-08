import glob
import logging
import time

from abstract import AbstractSensor, AbstractControl


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
