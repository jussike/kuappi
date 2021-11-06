import logging

from abstract import AbstractSwitch, AbstractControl
from config import CONFIG

if 'Wemo' in CONFIG.get('controls'):
    from controls.switches.wemo import Wemo
if 'KuappiGPIO' in CONFIG.get('controls'):
    from controls.switches.kuappigpio import KuappiGPIO
if 'NetSwitch' in CONFIG.get('controls'):
    from controls.switches.netswitch import NetSwitch
if 'NetControl' in CONFIG.get('controls'):
    from controls.netcontrol import NetControl
if 'ValloxControl' in CONFIG.get('controls'):
    from controls.valloxcontrol import ValloxControl
if 'AlarmControl' in CONFIG.get('controls'):
    from controls.alarmcontrol import AlarmControl


class Controller(AbstractControl, AbstractSwitch):
    def __init__(self):
        controls = []
        for control in CONFIG.get('controls'):
            cls = globals()[control]
            controls.append(cls())
            logging.info('Using control %s', control)
        self._controls = controls

    def on(self):
        for control in self._controls:
            if isinstance(control, AbstractSwitch):
                control.on()
            else:
                logging.error('%s is not instance of AbstractSwitch', control)

    def off(self):
        for control in self._controls:
            if isinstance(control, AbstractSwitch):
                control.off()
            else:
                logging.error('%s is not instance of AbstractSwitch', control)

    def cleanup(self):
        for output in self._controls:
            output.cleanup()

    @property
    def state(self):
        return all(v.state for v in self._controls)

    def control(self, param):
        if param is None:
            return
        if isinstance(param, bool):
            if param:
                self.on()
            else:
                self.off()
            return
        if isinstance(param, int):
          for control in self._controls:
              if isinstance(control, AbstractControl):
                  control.control(param)
              else:
                  logging.error('%s is not instance of AbstractControl', control)
