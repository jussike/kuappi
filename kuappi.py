import logging
from threading import Event
import signal

from config import CONFIG
from controls import Wemo, KuappiGPIO, OutputControl
from valloxcontrol import ValloxControl
from mitemp import MiTemp, MiTempControl
from temp import W1Temp, W1TempControl
from storage import Redis


def setup_logging(log_file=None):
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    logging.basicConfig(filename=log_file,
                        format=log_format,
                        level=logging.DEBUG)
    logging.info('Logging is set')


class Kuappi:
    def __init__(self):
        setup_logging('/tmp/log')
        self.redis = Redis()
        outputs = []
        for control in CONFIG.get('controls'):
            cls = globals()[control]
            outputs.append(cls())
            logging.info('Using control %s', control)
        self.output = OutputControl()
        self.output.set_outputs(outputs)
        sensor = CONFIG.get('sensor')
        sensor_cls = globals()[sensor]
        control_cls = globals()[sensor + 'Control']
        self.sensor = sensor_cls()
        self.control = control_cls()
        self.event = Event()
        signal.signal(signal.SIGTERM, self.cleanup)

    def loop(self):
        logging.info('Starting main loop')
        while not self.event.is_set():
            try:
                value = self.sensor.get_value()
                decision = self.control.get_decision(value, self.output.state)
                self.output.control(decision)
                logging.debug('%s %s' % (value, self.output.state))
                self.redis.add_multi((value, 1 if self.output.state else 0))
                self.event.wait(30)
            except KeyboardInterrupt:
                logging.info("stopping")
                self.output.cleanup()
                break
            except:
                logging.exception("Unknown exception")

    def cleanup(self, *_):
        self.output.cleanup()
        self.event.set()

Kuappi().loop()
