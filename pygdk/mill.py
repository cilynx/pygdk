import json
import math

from .machine import Machine
from .tool import Tool

RED    = '\033[31m'
ORANGE = '\033[91m'
YELLOW = '\033[93m'
GREEN  = '\033[92m'
CYAN   = '\033[36m'
ENDC   = '\033[0m'

################################################################################
# Initializer -- Load details from JSON
################################################################################

class Mill(Machine):
    def __init__(self, json_file):
        super().__init__(json_file)
        self.queue(comment='Loading Mill parameters from JSON', style='mill')
        with open(f"machines/{json_file}") as f:
            dict = json.load(f)
            if 'Tool Table' not in dict:
                raise KeyError(f"{RED}You machine configuration must reference a tool table file{ENDC}")
            with open(f"tables/{dict['Tool Table']}", 'r') as tt:
                self._tool_table = json.load(tt)
            self.max_rpm = dict['Max Spindle RPM']
            self.safe_z = 10 #TODO: This should be in a Workpiece class

################################################################################
# Constant Surface Speed
################################################################################

    @property
    def css(self):
        return self._css

    @css.setter
    def css(self, value):
        self.queue(comment=f"Desired Constant Surface Speed (CSS): {value:.4f} m/s | {value*196.85:.4f} ft/min{ENDC}", style='mill')
        self.queue(comment=f"Calculating RPM from CSS and tool diameter.", style='mill')
        rpm = value * 60000 / math.pi / self.tool.diameter
        if rpm > self.max_rpm:
            css = self.max_rpm * math.pi * self.tool.diameter / 60000
            self.queue(comment=f"{self.name} cannot do {rpm:.4f} rpm.  Maxing out at {self.max_rpm} rpm | {css:.4f} m/s | {css*196.85:.4f} ft/min", style='warning')
            rpm = self.max_rpm;
        self.queue(comment=f"Setting RPM: {rpm:.4f} | {rpm/60:.4f} Hz on the VFD", style='mill')
        self._rpm = rpm

    surface_speed = css

################################################################################
# Spindle Speed (S)
################################################################################

    @property
    def rpm(self):
        return self._rpm

    @rpm.setter
    def rpm(self, value):
        if value > self.max_rpm:
            raise ValueError(f"Machine.rpm ({value}) must be lower than Machine.max_rpm ({self.max_rpm})")
        self._rpm = value
        self.queue(code='G97', comment='Constant Spindle Speed')
        self.queue(code=f"S{value}", comment=f"Set Spindle RPM: {value:.4f}")
        if self.tool.diameter is not None:
            css = self.rpm * math.pi * self.tool.diameter / 60000
            if round(self._css, 4) != round(css, 4):
                self._css = css
                self.queue(comment=f"Calculated Tool Constant Surface Speed (CSS): {self.css:.4f} m/s | {self.css*196.85:.4f} ft/min", style='mill')
        else:
            self.queue(comment='Cannot calculate CSS from RPM because tool diameter is undefined', style='warning')

################################################################################
# Linear Interpolated Cuts (G1)
################################################################################

    cut = Machine.linear_interpolation
    icut = Machine.i_linear_interpolation
