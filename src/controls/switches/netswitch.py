import socket

from abstract import AbstractSwitch
from config import CONFIG

class NetSwitch(AbstractSwitch):
    def __init__(self):
        self.msg_on = bytes((1,))
        self.msg_off = bytes((0,))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = CONFIG.get('netctl_host')
        self.port = CONFIG.get('netctl_udp_port')
        self._state = None

    def on(self):
        self.socket.sendto(self.msg_on, (self.host, self.port))
        self._state = True

    def off(self):
        self.socket.sendto(self.msg_off, (self.host, self.port))
        self._state = False

    @property
    def state(self):
        return self._state

    def cleanup(self):
        self.off()
        self.socket.close()
