import glob
import time
import pywemo
import redis


current_millis = lambda: int(round(time.time() * 1000))

class Temp:
    def __init__(self):
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'

    def read_temp_raw(self):
        with open(self.device_file, 'r') as fh:
            return fh.readlines()
 
    def read_temp(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
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
        self.key = "temp"

    def add(self, temp):
        c_time = current_millis()
        self.redis.zadd(self.key, {"%s:%s" % (c_time, temp): c_time})

    def get_all(self):
        values = self.redis.zrangebyscore(self.key, 0, current_millis())
        return {k: v for i in values for k, v in zip([i.split(':')[0]],[i.split(':')[1]])}

def main():
    wemo = pywemo.discover_devices()
    if len(wemo) < 1:
        print ("kusi")
    wemo = wemo[0]
    redis = Redis()
    temp = Temp()

    for _ in range(5):
        _temp = temp.read_temp()
        redis.add(_temp)
        print (_temp)
        time.sleep(1)
        if temp.read_temp() > _temp:
            print ("nous")
            wemo.toggle()
    a=redis.get_all()
    print(a)

main()
