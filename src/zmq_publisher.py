from config import CONFIG
from threading import Thread, Event

import json
import logging
import queue
import zmq


class KuappiZMQSender:
    def __init__(self):
        self.alarm_sent = False
        self.port = "tcp://{}:{}".format(CONFIG.get('zmq_host'), CONFIG.get('zmq_send_port'))
        self.name = CONFIG.get('node_name')
        logging.info('Initializing KuappiZMQSender to %s with name %s', self.port, self.name)
        self.socket = zmq.Context().socket(zmq.PUB)
        self.socket.connect(self.port)
        self.event = Event()
        self.queue = queue.Queue(100)
        self.loop = Thread(
            target=self.sendloop,
            daemon=True)
        self.loop.start()

    def send(self, msg):
        try:
            self.queue.put_nowait(json.dumps({'sender': self.name, 'msg': msg}))
        except queue.Full:
            logging.error("Queue is full")

    def send_alarm(self, msg):
        if self.alarm_sent:
            return
        self.send(msg)
        # Assuming queue is not full
        self.alarm_sent = True

    def normal(self):
        if not self.alarm_sent:
            return
        self.send('Back to normal')
        self.alarm_sent = False

    def sendloop(self):
        while not self.event.is_set():
            item = self.get_item()
            if item:
                logging.info('sending %s', item)
                self.socket.send_string(item)

    def get_item(self):
        try:
            return self.queue.get(timeout=5)
        except queue.Empty:
            return None
