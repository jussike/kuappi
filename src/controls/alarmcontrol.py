from subprocess import Popen, DEVNULL
from threading import Thread, Event
from abstract import AbstractSwitch


class AlarmControl(AbstractSwitch):
    def __init__(self):
        self.loop = None
        self.proc = None
        self.event = Event()

    def on(self):
        if self.loop:
            return
        self.loop = Thread(
            target=self.alarmloop,
            daemon=True,
        )
        self.loop.start()

    def off(self):
        self.event.set()
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
            self.proc = None
        self.event.clear()
        self.loop = None

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
        return self.loop is not None

    def cleanup(self):
        self.off()
