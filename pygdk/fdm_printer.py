import json

from .machine import Machine

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
            dict = json.load(f)
            if 'Filament Table' not in dict:
                raise KeyError(f"{RED}Your machine configuration must reference a filament table file.  See https://github.com/cilynx/pygdk/blob/main/kossel.json for an example FDMPrinter configuration and https://github.com/cilynx/pygdk/blob/main/filament.json for an example filament table.{ENDC}")
            with open(f"tables/{dict['Filament Table']}", 'r') as ft:
                self.filament_table = json.load(ft)
