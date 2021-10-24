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
        self.queue(comment='Loading FDMPrinter parameters from JSON', style='fdm_printer')
        with open(f"machines/{json_file}") as f:
            if 'Filament Table' not in self.dict:
                raise KeyError(f"{RED}Your machine configuration must reference a filament table file.  See https://github.com/cilynx/pygdk/blob/main/kossel.json for an example FDMPrinter configuration and https://github.com/cilynx/pygdk/blob/main/filament.json for an example filament table.{ENDC}")
            with open(f"tables/{self.dict['Filament Table']}", 'r') as ft:
                self.filament_table = json.load(ft)
            self.nozzle_d = self.dict['Nozzle Diameter']
            self.retract_f = self.dict['Retraction']
            self.extra_push = self.dict['Extra Push']
            self.wait_for_bed = self.dict.get('Wait For Heated Bed', False)
            self._bed_temp = None
            self.wait_for_nozzle = self.dict.get('Wait For Nozzle', True)
            self._nozzle_temp = None
            if self.dict.get('Acceleration', None) is not None:
                self.accel = self['Acceleration']
            self.feed = self.dict['Max Feed Rate (mm/min)']
            for line in self.dict['Start G-Code']:
                self.queue(code=line[0], comment=line[1])

    def __del__(self):
        if hasattr(self, 'dict'):
            for line in self.dict.get('End G-Code', []):
                self.queue(code=line[0], comment=line[1])

    def squirtle(self, verbose=False):
        return Squirtle(self, verbose)

################################################################################
# Hot End and Bed Temperatures
################################################################################


    @property
    def nozzle_temp(self):
        if self._nozzle_temp is None:
            raise ValueError(f"{RED}Nozzle temperature must be set before it can be queried{ENDC}")
        return self._nozzle_temp

    @nozzle_temp.setter
    def nozzle_temp(self, temp_c):
        if self.wait_for_nozzle:
            self.queue(code='M109', s=temp_c, comment="Waiting for hotend to come up to temperature", style='fdm_printer')
        else:
            self.queue(code='M104', s=temp_c, comment="Setting hotend temperature and moving on", style='fdm_printer')
        self._nozzle_temp = temp_c

    @property
    def bed_temp(self):
        if self._bed_temp is None:
            raise ValueError(f"{RED}Bed temperature must be set before it can be queried{ENDC}")
        return self._bed_temp

    @bed_temp.setter
    def bed_temp(self, temp_c):
        if self.wait_for_bed:
            self.queue(code='M190', s=temp_c, comment="Waiting for bed to come up to temperature", style='fdm_printer')
        else:
            self.queue(code='M140', s=temp_c, comment="Setting bed temperature and moving on", style='fdm_printer')
