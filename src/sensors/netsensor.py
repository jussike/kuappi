import json
import logging
import socket
import time
from threading import Thread, Event

from abstract import AbstractSensor
from config import CONFIG


class NetSensor(AbstractSensor):

    BUFSIZE = 256
    MAX_DATA_AGE = 60 * 90
    def __init__(self, blocking=True):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(blocking)
        self.host = CONFIG.get('netctl_host')
        self.port = CONFIG.get('netctl_udp_port')
        logging.info('Initializing NetSensor for %s:%d', self.host, self.port)
        self.socket.bind((self.host, self.port))
        self.data = None
        self.data_time = None
        self.event = Event()
        self.loop = Thread(
            target=self.listener,
            daemon=True,
        )
        self.loop.start()

    def get_data(self):
        if not self.data:
            logging.info('NetSensor: no data, returning False')
            return False
        if time.monotonic() > self.data_time + self.MAX_DATA_AGE:
            logging.error('Too old data, returning False data')
            return False
        return self.data

    def listener(self):
        while not self.event.is_set():
            data = self.socket.recv(self.BUFSIZE)
            if data:
                self.data = json.loads(data)
                self.data_time = time.monotonic()

    def cleanup(self):
        self.event.set()
        self.data = None
