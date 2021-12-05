import logging
from threading import Event
import signal

from common import TEMP
from config import CONFIG

if 'MiTemp' == CONFIG.get('sensor'):
    from sensors.mitemp import MiTemp
if 'W1Temp' == CONFIG.get('sensor'):
    from sensors.w1temp import W1Temp
if 'MqttSensor' == CONFIG.get('sensor'):
    from sensors.mqtt import MqttSensor
if 'NetSensor' == CONFIG.get('sensor'):
    from sensors.netsensor import NetSensor
if 'FridgeDecision' == CONFIG.get('decision'):
    from decisions.fridgedecision import FridgeDecision
if 'FridgeAlarmDecision' == CONFIG.get('decision'):
    from decisions.fridgealarmdecision import FridgeAlarmDecision
if 'FreezerDecision' == CONFIG.get('decision'):
    from decisions.freezerdecision import FreezerDecision
if 'ValloxDecision' == CONFIG.get('decision'):
    from decisions.valloxdecision import ValloxDecision
if 'PassthruDecision' == CONFIG.get('decision'):
    from decisions.passthrudecision import PassthruDecision
if True == CONFIG.get('use_redis'):
    from storage.redis_storage import Redis
else:
    from storage.null_storage import NullStorage as Redis

from controller import Controller


def setup_logging(log_file=None):
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=log_file,
                        format=log_format,
                        force=True,
                        level=logging.INFO)
    logging.info('Logging is set')


class Kuappi:
    def __init__(self):
        setup_logging(CONFIG.get('log_file'))
        self.redis = Redis()
        self.controller = Controller()
        self.sensor = globals()[CONFIG.get('sensor')]()
        self.decision = globals()[CONFIG.get('decision')]()
        self.event = Event()
        signal.signal(signal.SIGTERM, self.cleanup)

    def loop(self):
        logging.info('Starting main loop')
        polling_freq = CONFIG.get('polling_freq', 60)
        while not self.event.is_set():
            try:
                data = self.sensor.get_data()
                if data is None:
                    self.event.wait(polling_freq)
                    continue
                decision = self.decision.get_decision(data, self.controller.state)
                self.controller.control(decision)
                if isinstance(data, dict) and TEMP in data.keys():
                    logging.debug('%s %s' % (data, self.controller.state))
                    self.redis.add_multi((data[TEMP], 1 if self.controller.state else 0))
                self.event.wait(polling_freq)
            except KeyboardInterrupt:
                logging.info("stopping")
                self.controller.cleanup()
                self.sensor.cleanup()
                break
            except Exception:
                logging.exception("Unknown exception")

    def cleanup(self, *_):
        self.controller.cleanup()
        self.sensor.cleanup()
        self.event.set()

Kuappi().loop()
