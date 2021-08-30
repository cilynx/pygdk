import json
import os
import sys

from .tool import Tool

MACHINE = '\033[91m'
ENDC = '\033[0m'

class Machine:

    MILL = 'Mill'
    LATHE = 'Lathe'

################################################################################
# Initializer -- Load details from JSON or populate from passed parameters
################################################################################

    def __init__(self, name=None, type=None, max_feed=None):
        if os.path.exists(name):
            if type is not None or max_feed is not None:
                raise ValueError(f"Machine must be initialized by JSON or parameters, but not both")
            print(f";{MACHINE} Loading Machine parameters from JSON{ENDC}")
            with open(name) as f:
                dict = json.load(f)
                name = dict['Name']
                type = dict['Type']
                max_feed = dict['Max Feed Rate (mm/min)']
                self._max_rpm = dict['Max Spindle RPM']
                if 'Tool Table' in dict:
                    tt_file = dict['Tool Table']
                    if os.path.exists(tt_file):
                        with open(tt_file, 'r') as tt:
                            self._tool_table = json.load(tt)
                    else:
                        raise ValueError(f"No such file: {tt_file}")
                else:
                    self._tool_table = None
        if not type in [self.MILL, self.LATHE]:
            raise ValueError(f"Machine type ({type}) must be Machine.MILL or Machine.LATHE")
        self._type = type
        self._max_feed = max_feed
        if name is None:
            self._name = type
        else:
            self._name = name
        print(f";{MACHINE} Initializing a {self.type} named {self.name}{ENDC}")

################################################################################
# Print and persist Machine parameters as JSON
################################################################################

    @property
    def json(self):
        dict = {
            "Name": self._name,
            "Type": self._type,
            "Max Feed Rate (mm/min)": self._max_feed,
            "Max Spindle RPM": self._max_rpm
        }
        return json.dumps(dict, indent=2)

    def save_json(self, file, prompt=True):
        if prompt and os.path.exists(file):
            print(f"Overwrite {file}? (y/n) ")
            response = sys.stdin.read(1)
            if response != 'y':
                return
        f = open(file, 'w')
        f.write(self.json + '\n')
        f.close()

################################################################################
# CAMotics-compatible Tool Table
################################################################################

    def new_tool(self):
        return Tool(self)

    def load_tools(self, file):
        with open(file) as f:
            self._tool_table = json.load(f)

    def tool(self, i):
        if self._tool_table:
            if str(i) in self._tool_table:
                return Tool(self, self._tool_table[str(i)], str(i))
            else:
                raise ValueError(f"Tool {i} is not in the Tool Table")
        else:
            raise ValueError(f"Must load Tool Table before using it")

################################################################################
# Machine.type -- 'Mill' or 'Lathe'.  Determines how CSS is calculated.
################################################################################

    @property
    def type(self):
        return self._type

    @type.setter
    def name (self, value):
        print(f";{MACHINE} Setting {self.name} machine type: {value}{ENDC}")
        self._type = value

################################################################################
# Machine.name -- Only used for display, to make things more human-friendly.
################################################################################

    @property
    def name(self):
        return self._name

    @name.setter
    def name (self, value):
        print(f";{MACHINE} Renaming {self.name}: {value}{ENDC}")
        self._name = value

################################################################################
# Machine.safe_z -- This probably belongs in a Workpiece class, not here
################################################################################

    @property
    def safe_z(self):
        return self._safe_z

    @safe_z.setter
    def safe_z (self, value):
        print(f";{MACHINE} Setting {self.name} Safe Z: {value}{ENDC}")
        self._safe_z = value

################################################################################
# Machine.max_rpm -- Used in speeds and feeds calculations.
################################################################################

    @property
    def max_rpm(self):
        return self._max_rpm

    @max_rpm.setter
    def max_rpm(self, value):
        print(f";{MACHINE} Setting {self.name} max Spindle RPM: {value}{ENDC}")
        self._max_rpm = value

################################################################################
# Machine.max_feed -- Used for rapids by default.
################################################################################

    @property
    def max_feed(self):
        return self._max_feed

    @max_feed.setter
    def max_feed(self, value):
        print(f";{MACHINE} Setting {self.name} max Feed: {value}mm/min{ENDC}")
        self._max_feed = value
