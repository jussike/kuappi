import json
import logging
import socket

from abstract import AbstractControl
from config import CONFIG


class NetControl(AbstractControl):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = CONFIG.get('netctl_host')
        self.port = CONFIG.get('netctl_udp_port')
        self._state = None

    def control(self, value):
        self.socket.sendto(json.dumps(value).encode(), (self.host, self.port))
        self._state = value

    @property
    def state(self):
        return self._state

    def cleanup(self):
        self.socket.close()
