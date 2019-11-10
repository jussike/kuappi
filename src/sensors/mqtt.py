import json
import logging
import paho.mqtt.client as mqtt

from abstract import AbstractSensor
from config import CONFIG

class MqttSensor(AbstractSensor):
    def __init__(self):
        self.client_id = CONFIG.get('mqtt_client')
        self.data = None

        client = mqtt.Client('Kuappi')
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect("localhost", 1883, 60)
        client.loop_start()

    def get_data(self):
        return self.data

    def on_connect(self, client, userdata, flags, rc):
        logging.info("Connected with result code %d", rc)
        client.subscribe(self.client_id)

    def on_message(self, client, userdata, msg):
        data = json.loads(msg.payload.decode('utf-8'))
        self.data = data
