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
            self.bowden_length = self.dict['Bowden Length']
            self.retract_f = self.dict['Retraction']
            self.extra_push = self.dict['Extra Push']
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
# Load and Unload Filament
################################################################################

    def load_filament(self, prime=100):
        self.queue(code='G0', x=0, y=0, z=10, f=self.max_feed, comment="Straighten bowden tube")
        self.queue(code='G0', e=self.bowden_length, f=3000, comment="Load filament")
        self.wait_for_nozzle_temp(220)
        if prime:
            self.queue(code='G0', e=self.bowden_length+prime, f=300, comment="Load filament")

    def unload_filament(self):
        self.queue(code='G0', x=0, y=0, z=10, f=max_feed, comment="Straighten bowden tube")
        self.queue(code='G0', e=-self.dict['Bowden Length'], f=3000, comment="Unload filament")
        self.wait_for_nozzle_temp(220)

################################################################################
# Hot End and Bed Temperatures
################################################################################

    def set_nozzle_temp(self, deg_c):
        self.queue(code='M104', s=deg_c, comment=f"Set hotend to {deg_c}C and move on", style='fdm_printer')

    def wait_for_nozzle_temp(self, deg_c):
        self.queue(code='M109', s=deg_c, comment=f"Wait for hotend to get to {deg_c}C", style='fdm_printer')

    def set_bed_temp(self, deg_c):
        self.queue(code='M140', s=deg_c, comment=f"Set bed to {deg_c}C and move on", style='fdm_printer')

    def wait_for_bed_temp(self, deg_c):
        self.queue(code='M190', s=deg_c, comment=f"Wait for bed to get to {deg_c}C", style='fdm_printer')
