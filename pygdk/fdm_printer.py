import json

from .machine import Machine
from .turtle import Squirtle

RED    = '\033[31m'
ORANGE = '\033[91m'
YELLOW = '\033[93m'
GREEN  = '\033[92m'
CYAN   = '\033[36m'
ENDC   = '\033[0m'

################################################################################
# Initializer -- Load details from JSON
################################################################################

class FDMPrinter(Machine):
    def __init__(self, json_file):
        super().__init__(json_file)
        print(f";{YELLOW} Loading FDMPrinter parameters from JSON{ENDC}")
        with open(f"machines/{json_file}") as f:
            self.dict = json.load(f)
            if 'Filament Table' not in self.dict:
                raise KeyError(f"{RED}Your machine configuration must reference a filament table file.  See https://github.com/cilynx/pygdk/blob/main/kossel.json for an example FDMPrinter configuration and https://github.com/cilynx/pygdk/blob/main/filament.json for an example filament table.{ENDC}")
            with open(f"tables/{self.dict['Filament Table']}", 'r') as ft:
                self.filament_table = json.load(ft)
            self.nozzle_d = self.dict['Nozzle Diameter']
            self.retract_f = self.dict['Retraction']
            self.extra_push = self.dict['Extra Push']
            self.feed = self.dict['Max Feed Rate (mm/min)']
            for line in self.dict['Start G-Code']:
                print(f"{line[0]} ;{GREEN} {line[1]}{ENDC}")

    def __del__(self):
        for line in self.dict['End G-Code']:
            print(f"{line[0]} ;{GREEN} {line[1]}{ENDC}")

    def squirtle(self, verbose=False):
        return Squirtle(self, verbose)

################################################################################
# Hot End and Bed Temperatures
################################################################################

    def nozzle_temp(self, temp_c, block):
        if block:
            print(f"M109 S{temp_c} ;{RED} Waiting for hotend to come up to temperature{ENDC}")
        else:
            print(f"M104 S{temp_c} ;{ORANGE} Setting hotend temperature and moving on{ENDC}")

    def bed_temp(self, temp_c, block):
        if block:
            print(f"M190 S{temp_c} ;{RED} Waiting for bed to come up to temperature{ENDC}")
        else:
            print(f"M140 S{temp_c} ;{ORANGE} Setting bed temperature and moving on{ENDC}")
