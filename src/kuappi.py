import logging
from threading import Event
import signal

from config import CONFIG

if 'Wemo' in CONFIG.get('controls'):
    from controls.switches.wemo import Wemo
if 'KuappiGPIO' in CONFIG.get('controls'):
    from controls.switches.kuappigpio import KuappiGPIO
if 'MiTemp' == CONFIG.get('sensor'):
    from sensors.mitemp import MiTemp
if 'W1Temp' == CONFIG.get('sensor'):
    from sensors.w1temp import W1Temp
if 'FridgeDecision' == CONFIG.get('decision'):
    from decisions.fridgedecision import FridgeDecision
if 'ValloxDecision' == CONFIG.get('decision'):
    from decisions.valloxdecision import ValloxDecision
if 'use_redis' == True:
    from storage.redis_storage import Redis
else:
    from storage.null_storage import NullStorage as Redis

from controller import Controller


def setup_logging(log_file=None):
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=log_file,
                        format=log_format,
                        level=logging.DEBUG)
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
                value = self.sensor.get_value()
                decision = self.decision.get_decision(value, self.controller.state)
                self.controller.control(decision)
                logging.debug('%s %s' % (value, self.controller.state))
                self.redis.add_multi((value, 1 if self.controller.state else 0))
                self.event.wait(polling_freq)
            except KeyboardInterrupt:
                logging.info("stopping")
                self.controller.cleanup()
                break
            except:
                logging.exception("Unknown exception")

    def cleanup(self, *_):
        self.controller.cleanup()
        self.event.set()

Kuappi().loop()
