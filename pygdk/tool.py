RED  = '\033[31m' # Red
YELLOW = '\033[93m' # Yellow
ENDC  = '\033[0m'  # End Color

class Tool:

################################################################################
# Tool.__init__() -- Initialize based on parameter dictionary
################################################################################

    def __init__(self, machine, dict=None, i=None):
        if dict and i:
            self._rpm = dict.get('rpm', None)
            self._ipm = dict.get('ipm', None)
            self._units = dict.get('units', None)
            self._shape = dict.get('shape', None)
            self._length = dict.get('length', None)
            self._diameter = dict.get('diameter', None)
            self._description = dict.get('description', None)
            self._number = i
            diameter = self._diameter * (25.4 if self._units == 'imperial' else 1)
            print(f";{YELLOW} Looking up Tool {i} in Tool Table: [{self._description}] | {diameter:.4f} mm{ENDC}")

################################################################################
# Tool.number -- Tool Table Index
################################################################################

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, number):
        self._number = number

################################################################################
# Tool.diameter -- Diameter of the Tool
################################################################################

    @property
    def diameter(self):
        if hasattr(self, '_diameter') and self._diameter is not None:
            return self._diameter * (25.4 if self._units == 'imperial' else 1)
        else:
            return ValueError(f"{RED}Tool.diameter must be set (directly or indirectly) before it is referenced{ENDC}")

    @diameter.setter
    def diameter(self, value):
        self._diameter = value
        print(f";{YELLOW} Setting Tool Diameter: {self.diameter} mm | {self.diameter/25.4}\"{ENDC}")

################################################################################
# Tool.length -- Length of the Tool
################################################################################

    @property
    def length(self):
        if hasattr(self, '_length') and self._length is not None:
            return self._length * (25.4 if self._units == 'imperial' else 1)
        else:
            return ValueError(f"{RED}Tool.length must be set (directly or indirectly) before it is referenced{ENDC}")

    @length.setter
    def length(self, value):
        self._length = value
        print(f";{YELLOW} Setting Tool Length: {self.length} mm | {self.length/25.4}\"{ENDC}")

################################################################################
# Tool.flutes -- Number of Flutes
################################################################################

    @property
    def flutes(self):
        return int(self._description.split(',')[1].replace('Flutes',''))

################################################################################
# Tool.material -- HSS, Carbide, etc.
################################################################################

    @property
    def material(self):
        return self._description.split(',')[3].strip()

################################################################################
# Tool.ipm -- Manufacturer-Recommended Inches-Per-Minute Feed
################################################################################

    @property
    def ipm(self):
        return self._ipm

################################################################################
# Tool.rpm -- Manufacturer-Recommended Spindle RPM
################################################################################

    @property
    def rpm(self):
        return self._rpm
