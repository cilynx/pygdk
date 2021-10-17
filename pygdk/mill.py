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
        print(f";{YELLOW} Loading Mill parameters from JSON{ENDC}")
        with open(json_file) as f:
            dict = json.load(f)
            if 'Tool Table' not in dict:
                raise KeyError(f"{RED}You machine configuration must reference a tool table file{ENDC}")
            with open(dict['Tool Table'], 'r') as tt:
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
        print(f";{YELLOW} Desired Constant Surface Speed (CSS): {value:.4f} m/s | {value*196.85:.4f} ft/min{ENDC}")
        print(f";{YELLOW} Calculating RPM from CSS and tool diameter.{ENDC}")
        rpm = value * 60000 / math.pi / self.tool.diameter
        if rpm > self.max_rpm:
            css = self.max_rpm * math.pi * self.tool.diameter / 60000
            print(f";{RED} {self.name} cannot do {rpm:.4f} rpm.  Maxing out at {self.max_rpm} rpm | {css:.4f} m/s | {css*196.85:.4f} ft/min{ENDC}")
            rpm = self.max_rpm;
        print(f";{YELLOW} Setting RPM: {rpm:.4f} | {rpm/60:.4f} Hz on the VFD{ENDC}")
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
        print(f"G97 ;{GREEN} Constant Spindle Speed{ENDC}")
        print(f"S{value:.4f} ;{GREEN} Set Spindle RPM: {value:.4f}{ENDC}")
        if self.tool.diameter is not None:
            css = self.rpm * math.pi * self.tool.diameter / 60000
            if round(self._css, 4) != round(css, 4):
                self._css = css
                print(f";{YELLOW} Calculated Tool Constant Surface Speed (CSS): {self.css:.4f} m/s | {self.css*196.85:.4f} ft/min{ENDC}")
        else:
            print(f";{RED} Cannot calculate CSS from RPM because tool diameter is undefined{ENDC}")
        # TODO: Move this out to shared feeds-and-speeds routine
        # chip_load = 0.1 # mm/flute
        # if chip_load is not None:
        #     feed = chip_load * self.tool.flutes * self.rpm # mm/min
        #     print(f";{YELLOW} Calculated feed from chip load, flutes, and RPM: {feed:.4f} mm/min | {feed/304.8:.4f} ft/min{ENDC}")
        #     if feed > self.max_feed:
        #         print(f";{RED} {self.name} cannot feed at {feed:.4f} mm/min.  Maxing out at {self.max_feed} mm/min{ENDC}")
        #         feed = self.max_feed
        #     self.feed = feed

################################################################################
# Linear Interpolated Cuts (G1)
################################################################################

    cut = Machine.linear_interpolation
    icut = Machine.i_linear_interpolation
