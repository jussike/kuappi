import logging

from abstract import AbstractSwitch, AbstractControl


class Controller(AbstractControl, AbstractSwitch):
    def __init__(self, controls=None):
        self.controls = controls

    def set_controls(self, controls):
        self.controls = controls

    def on(self):
        for control in self.controls:
            if isinstance(control, AbstractSwitch):
                control.on()
            else:
                logging.error('%s is not instance of AbstractSwitch', control)

    def off(self):
        for control in self.controls:
            if isinstance(control, AbstractSwitch):
                control.off()
            else:
                logging.error('%s is not instance of AbstractSwitch', control)

    def cleanup(self):
        for output in self.controls:
            if isinstance(output, AbstractSwitch):
                output.cleanup()
            # Other types of controls don't need this cleanup

    @property
    def state(self):
        return all(v.state for v in self.controls)

    def control(self, param):
        if param is True:
            self.on()
        elif param is False:
            self.off()
        elif isinstance(param, int):
            for control in self.controls:
                if isinstance(control, AbstractControl):
                    control.control(param)
                else:
                    logging.error('%s is not instance of AbstractControl', control)
