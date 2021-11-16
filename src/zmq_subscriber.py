from config import CONFIG
from threading import Thread, Event

import json
import logging
import zmq


class KuappiZMQReceiver:
    def __init__(self):
        self.port = "tcp://{}:{}".format(CONFIG.get('zmq_host'), CONFIG.get('zmq_recv_port'))
        logging.info('Initializing KuappiZMQReceiver to %s', self.port)
        self.socket = zmq.Context().socket(zmq.SUB)
        self.socket.connect(self.port)
        self.socket.setsockopt(zmq.SUBSCRIBE, b"")
        self.event = Event()
        self.loop = Thread(
            target=self.recvloop,
            daemon=True,
        )
        self.loop.start()
        self.subscribers = []

    def register(self, sub):
        self.subscribers.append(sub)

    def recvloop(self):
        while not self.event.is_set():
            try:
                data = json.loads(self.socket.recv())
            except Exception:
                logging.info('Garbage received')
                continue
            for subscriber in self.subscribers:
                subscriber.on_message(data)
