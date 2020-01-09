import logging
import time
import signal

from config import CONFIG
from controls import Wemo, KuappiGPIO, OutputControl
from temp import Temp, TempControl
from storage import Redis


def setup_logging(log_file=None):
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    logging.basicConfig(filename=log_file,
                        format=log_format,
                        level=logging.DEBUG)
    logging.info('Logging is set')


def create_instance(sensor_class):
    return sensor_class()


class Kuappi:
    def __init__(self):
        setup_logging('/tmp/log')
        self.redis = Redis()
        outputs = []
        if 'pywemo' in CONFIG.get('controls'):
            outputs.append(Wemo())
            logging.info('Controlling wemo switch')
        if 'rpi_gpio' in CONFIG.get('controls'):
            outputs.append(KuappiGPIO())
            logging.info('Controlling GPIO')
        self.output = OutputControl()
        self.output.set_outputs(outputs)
        self.sensor = create_instance(Temp)
        self.control = create_instance(TempControl)
        signal.signal(signal.SIGTERM, self.output.cleanup)

    def loop(self):
        logging.info('Starting main loop')
        while True:
            try:
                value = self.sensor.get_value()
                if self.control.get_decision(value, self.output.state) is True:
                    self.output.on()
                elif self.control.get_decision(value, self.output.state) is False:
                    self.output.off()
                logging.debug('%s %s' % (value, self.output.state))
                self.redis.add_multi((value, 1 if self.output.state else 0))
                time.sleep(30)
            except KeyboardInterrupt:
                logging.info("stopping")
                self.output.cleanup()
                break
            except:
                logging.exception("Unknown exception")

Kuappi().loop()
