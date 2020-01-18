import logging
import serial
import time
import threading

from abstract import AbstractSwitch, AbstractControl


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
    speeds = {
              1: b'\x01\x22\x11\x29\x01\x5e',
              2: b'\x01\x22\x11\x29\x03\x60',
              3: b'\x01\x22\x11\x29\x07\x64',
              4: b'\x01\x22\x11\x29\x0f\x6c',
              5: b'\x01\x22\x11\x29\x1f\x7c',
              6: b'\x01\x22\x11\x29\x3f\x9c',
              7: b'\x01\x22\x11\x29\x7f\xdc',
              8: b'\x01\x22\x11\x29\xff\x5c',
    }

    broadcast_speeds = {
              1: b'\x01\x22\x20\x29\x01\x6d',
              2: b'\x01\x22\x20\x29\x03\x6f',
              3: b'\x01\x22\x20\x29\x07\x73',
              4: b'\x01\x22\x20\x29\x0f\x7b',
              5: b'\x01\x22\x20\x29\x1f\x8b',
              6: b'\x01\x22\x20\x29\x3f\xab',
              7: b'\x01\x22\x20\x29\x7f\xeb',
              8: b'\x01\x22\x20\x29\xff\x6b',
    }

    def __init__(self, control):
        self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.1)
        self.control = control
        self.checksum_byte = None

    def set_speed(self, speed):
        control_data = self.speeds[speed]
        self.ser.write(control_data)
        self.listen_ack(control_data[-1], speed)

    def listen_ack(self, checksum, state):
        listen_thread = threading.Thread(target=self.run, args=(checksum, state))
        listen_thread.start()

    def inform_remotes(self, speed):
        control_data = self.broadcast_speeds[speed]
        self.ser.write(control_data)

    def run(self, checksum, state):
        data = b''
        while True:
            while self.ser.in_waiting:
                data += self.ser.read()
            if len(data) > 0:
                for byte in data:
                    if byte == checksum:
                        self.control.state = state
                        self.inform_remotes(state)
                        return
            time.sleep(0.1)

#echo -ne '\x01\x22\x10\x29\x07\x63' | cat >/dev/ttyUSB0
#ed           01  11  22  08  01  3d
#ser.write(b'\x01\x22\x11\x00\x71\xa5') # 01 11 22 71 e5 8a
#ser.write(b'\x01\x22\x11\x00\x79\xad')
# kysy I/O
#ser.write(b'\x01\x22\x11\x00\x08\x3c') # 01112208013d
#kysy huoltomuistutin
#ser.write(b'\x01\x22\x11\x00\xa6\xda')
#aseta huoltomuistutin
#ser.write(b'\x01\x22\x11\xa6\x06\xe0')

#ser.write(b'\x01\x22\x11\x00\xab\xdf')
#ser.write(b'\x01\x22\x11\xab\x05\xe4')

#ser.write(b'\x01\x22\x11\x08\x01\x3d')

#ser.write(b'\x01\x22\x11\x08\x08\x44')
#ser.write(b'\x01\x22\x11\x08\x28\x64')
