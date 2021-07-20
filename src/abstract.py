from abc import ABCMeta, abstractmethod, abstractproperty


class AbstractSensor(metaclass=ABCMeta):
    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

class AbstractDecision(metaclass=ABCMeta):
    @abstractmethod
    def get_decision(self, data, state=None):
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
