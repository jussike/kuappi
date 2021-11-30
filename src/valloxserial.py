import logging
import serial
import time
import threading


class ValloxSerial:
    system = b'\x01'
    sender = b'\x22'
    destinations = {
        'host': b'\x11',
        'remote_broadcast': b'\x20',
    }
    commands = {
        'speed': b'\x29',
        'intake_temp': b'\x5b',
        'select': b'\xa3',
    }
    # There are wrong temp variables in spec:
    # Proper variables: 5a 5b 5c 58, Remote control shows 5b
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
        },
    }
    timeout = 0.05

    def __init__(self):
        logging.info('Initializing vallox serial')
        self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.02)
        self.checksum_byte = None
        self.lock = threading.RLock()

    def get_request_data(self, destination, command):
        request_data = self.system \
                       + self.sender \
                       + self.destinations[destination] \
                       + bytes((0,)) \
                       + self.commands[command]
        request_data += self.get_checksum(request_data)
        return request_data

    def get_control_data(self, destination, command, value, value_pass=None):
        control_data = self.system \
                       + self.sender \
                       + self.destinations[destination] \
                       + self.commands[command]
        if value_pass:
            control_data += bytes((value,))
        else:
            control_data += self.values[command][value]

        control_data += self.get_checksum(control_data)
        return control_data

    def get_checksum(self, serial_data):
        checksum = 0
        for byte in serial_data:
            checksum += byte
        checksum = checksum & 0xff
        return bytes((checksum,))

    def reset(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    def set_speed(self, speed):
        select = self.ask_vallox('select')
        if not select & 1:
            self.power_on()
        self.set_attribute('speed', speed)

    def power_off(self):
        value = self.ask_vallox('select')
        value = value & ~1
        self.set_attribute('select', value, value_pass=True)

    def power_on(self):
        value = self.ask_vallox('select')
        value = value | 1
        self.set_attribute('select', value, value_pass=True)

    def set_attribute(self, attribute, value, value_pass=None):
        control_data = self.get_control_data('host', attribute, value, value_pass)
        with self.lock:
            self.reset()
            self.ser.write(control_data)
            self.listen_ack(control_data[-1], attribute, value)

    def listen_ack(self, checksum, attribute, state):
        listen_thread = threading.Thread(target=self.run, args=(checksum, attribute, state))
        listen_thread.start()

    def inform_remotes(self, attribute, value):
        control_data = self.get_control_data('remote_broadcast', attribute, value, value_pass=(attribute=='select'))
        self.ser.write(control_data)

    def run(self, checksum, attribute, state):
        if not self.wait_for_ack(checksum):
            logging.error('Missing ack')
            return
        self.control.state = state
        self.inform_remotes(attribute, state)

    def wait_for_ack(self, checksum):
        started = time.monotonic()
        while time.monotonic() < started + self.timeout:
            response = self.wait_for_response(1)[0]
            if response == checksum:
                return True
            logging.error('Discarding invalid ack, received %d, expected %d', response, checksum)
        return False

    def wait_for_response(self, length=None):
        with self.lock:
            data = b''
            started = time.monotonic()
            while time.monotonic() < started + self.timeout:
                while self.ser.in_waiting:
                    data += self.ser.read()
                if len(data) == 0:
                    continue
                elif length and len(data) == length:
                    # Length based data (e.g. ACK)
                    return data
                elif not length and data[0] != self.system[0]:
                    logging.error('Flushing data %s %d', data, len(data))
                    data = b''
                    continue
                checksum = self.get_checksum(data[0:-1])[0]
                if checksum == data[-1]:
                    return data
        logging.error('timeout')
        return data

    def ask_vallox(self, attribute):
        req_data = self.get_request_data('host', attribute)
        with self.lock:
            self.reset()
            self.ser.write(req_data)
            data = self.wait_for_response()
        if len(data) == 6:
            return data[4]
        return None

    def vallox_speed_value_to_number(self, value):
        return bin(value).count("1")


vallox_serial = ValloxSerial()
