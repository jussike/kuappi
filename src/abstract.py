from abc import ABCMeta, abstractmethod, abstractproperty

from zmq_subscriber import KuappiZMQReceiver
from zmq_publisher import KuappiZMQSender

import logging
import time


class AbstractSensor(metaclass=ABCMeta):
    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass


class AbstractDecision(metaclass=ABCMeta):
    DEFAULT_CONTROL_TIME = 60 * 30

    @abstractmethod
    def get_decision(self, data, state=None):
        pass

    def __init__(self, zmq=False):
        logging.info('Initializing decision super class')
        self._remote_controlled = None
        self.remote_control_decision = False
        self.control_time = self.DEFAULT_CONTROL_TIME
        if zmq:
            self.zmq_sub = KuappiZMQReceiver()
            self.zmq_sub.register(self)
            self.zmq_pub = KuappiZMQSender()

    def control(self, decision=None, control_time=None):
        self.remote_control_decision = decision if decision is not None else False
        self.control_time = control_time if control_time else self.DEFAULT_CONTROL_TIME
        self._remote_controlled = time.monotonic()

    @property
    def remote_controlled(self):
        if not self._remote_controlled:
            return False
        if time.monotonic() < self._remote_controlled + self.control_time:
            return True
        self._remote_controlled = None
        return False

    def on_message(self, msg):
        cmd = 'remote_' + msg['cmd']
        kwargs = msg['params'] if 'params' in msg else {}

        if cmd in self.__class__.__dict__.keys():
            self.__class__.__dict__[cmd](self, **kwargs)
        else:
            logging.error('%s not found on class %s', cmd, self.__class__.__name__)


class AbstractSwitch(metaclass=ABCMeta):
    @abstractmethod
    def on(self):
        pass

    @abstractmethod
    def off(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @property
    @abstractmethod
    def state(self):
        pass


class AbstractControl(metaclass=ABCMeta):
    @abstractmethod
    def control(self, param):
        pass

    @property
    @abstractmethod
    def state(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass
