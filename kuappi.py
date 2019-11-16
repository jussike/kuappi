import glob
import time
import pywemo
import redis


current_millis = lambda: int(round(time.time() * 1000))

class Temp:
    soft_hi_limit = 5
    soft_low_limit = 3
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
            print('error reading raw data')
 
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
            print(e)

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
            print('wemo error')

    def off(self):
        try:
            self.wemo.off()
            self.state = False
        except:
            print('wemo error')

def main():
    redis = Redis()
    temp = Temp()
    wemo = Wemo()

    while True:
        try:
            _temp = temp.read_temp()
            if _temp >= temp.soft_hi_limit and wemo.state is False:
                wemo.on()
            elif _temp <= temp.soft_low_limit and wemo.state is True:
                wemo.off()
            elif _temp > temp.hard_hi_limit:
                wemo.on()
            elif _temp < temp.hard_low_limit:
                wemo.off()
            print('%s %s' % (_temp, wemo.state))
            redis.add_multi([_temp, 1 if wemo.state else 0])
            time.sleep(10)
        except KeyboardInterrupt:
            print("stopping")
            break

main()
