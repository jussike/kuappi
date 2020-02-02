import logging
import redis
import time

current_millis = lambda: int(round(time.time() * 1000))


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
