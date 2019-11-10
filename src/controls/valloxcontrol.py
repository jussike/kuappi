import logging
import serial
import time
import threading

from abstract import AbstractControl


class ValloxControl(AbstractControl):
    def __init__(self):
        self.serial = ValloxSerial(self)
        self._speed = None

    @property
    def state(self):
        return self._speed

    @state.setter
    def state(self, state):
        self._speed = state

    def control(self, speed):
        if speed != self._speed:
            self.serial.set_speed(speed)


class ValloxSerial:
    system = b'\x01'
    sender = b'\x22'
    destinations = {
        'host': b'\x11',
        'remote_broadcast': b'\x20',
    }
    commands = {
        'speed': b'\x29',
    }
    values = {
        'speed': {
            1: b'\x01',
            2: b'\x03',
            3: b'\x07',
            4: b'\x0f',
            5: b'\x1f',
            6: b'\x3f',
            7: b'\x7f',
            8: b'\xff',
        }
    }
    timeout = 3

    def __init__(self, control):
        self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.1)
        self.control = control
        self.checksum_byte = None
        self.lock = threading.RLock()

    def get_control_data(self, destination, command, value):
        control_data = self.system \
                       + self.sender \
                       + self.destinations[destination] \
                       + self.commands[command] \
                       + self.values[command][value]
        checksum = 0
        for byte in control_data:
            checksum += byte
        checksum = checksum & 0xff
        control_data += bytes((checksum,))
        return control_data

    def set_speed(self, speed):
        control_data = self.get_control_data('host', 'speed', speed)
        with self.lock:
            self.ser.write(control_data)
            self.listen_ack(control_data[-1], speed)

    def listen_ack(self, checksum, state):
        listen_thread = threading.Thread(target=self.run, args=(checksum, state))
        listen_thread.start()

    def inform_remotes(self, speed):
        control_data = self.get_control_data('remote_broadcast', 'speed', speed)
        self.ser.write(control_data)

    def run(self, checksum, state):
        with self.lock:
            data = b''
            started = time.monotonic()
            while time.monotonic() < started + self.timeout:
                while self.ser.in_waiting:
                    data += self.ser.read()
                if len(data) == 0:
                    time.sleep(0.1)
                    continue
                for byte in data:
                    if byte == checksum:
                        self.control.state = state
                        self.inform_remotes(state)
                        return
