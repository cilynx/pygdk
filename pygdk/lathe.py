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

class Lathe(Machine):
    def __init__(self, json_file):
        super().__init__(json_file)
        print(f";{YELLOW} Loading Lathe parameters from JSON{ENDC}")
        with open(f"machines/{json_file}") as f:
            dict = json.load(f)
            if 'Tool Table' not in dict:
                raise KeyError(f"{RED}You machine configuration must reference a tool table file{ENDC}")
            with open(f"tables/{dict['Tool Table']}", 'r') as tt:
                self._tool_table = json.load(tt)
            self.max_rpm = dict['Max Spindle RPM']
