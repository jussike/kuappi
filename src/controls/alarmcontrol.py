from subprocess import Popen, DEVNULL
from threading import Thread, Event
from abstract import AbstractControl


class AlarmControl(AbstractControl):
    def __init__(self):
        self.loop = None
        self.proc = None
        self.event = Event()
        self._state = False

    def alarm_on(self):
        if self.loop:
            return
        self.loop = Thread(
            target=self.alarmloop,
            daemon=True,
        )
        self.loop.start()

    def alarm_off(self):
        self.event.set()
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
            self.proc = None
        self.event.clear()
        self.loop = None

    def control(self, decision):
        if decision:
            self.alarm_on()
        else:
            self.alarm_off()
        self._state = decision

    def alarmloop(self):
        while not self.event.is_set():
            self.proc = Popen(
                ["mpg123", "controls/alarm.mp3"],
                stdout=DEVNULL,
                stderr=DEVNULL,
            )
            self.proc.wait()

    @property
    def state(self):
        return self._state
