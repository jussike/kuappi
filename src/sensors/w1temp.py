import glob
import logging
import time

from abstract import AbstractSensor
from common import TEMP

class W1Temp(AbstractSensor):
    def __init__(self):
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'

    def read_temp_raw(self):
        try:
            with open(self.device_file, 'r') as fh:
                return fh.readlines()
        except Exception:
            logging.exception('error reading raw data')

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

    def get_data(self):
        return {TEMP: self.read_temp()}

    def cleanup(self):
        pass
