from abc import ABCMeta, abstractmethod, abstractproperty


class AbstractSensor(metaclass=ABCMeta):
    @abstractmethod
    def get_value():
        pass


class AbstractDecision(metaclass=ABCMeta):
    @abstractmethod
    def get_decision(self, value, state=None):
        pass


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


class AbstractControl(metaclass=ABCMeta):
    @abstractmethod
    def control(self, param):
        pass
