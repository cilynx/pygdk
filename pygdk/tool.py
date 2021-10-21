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
            self._shank = dict.get('shank', None)
            self._flutes = dict.get('flutes', None)
            self._length = dict.get('length', None)
            self._diameter = dict.get('diameter', None)
            self._description = dict.get('description', None)
            self._flute_length = dict.get('flute_length', None)
            self._number = i
            self.machine = machine
            diameter = self._diameter * (25.4 if self._units == 'imperial' else 1)
            machine.queue(comment=f"Looking up Tool {i} in Tool Table: [{self._description}] | {diameter:.4f} mm", style='tool')

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
# Tool Diameter
################################################################################

    @property
    def diameter(self):
        if self._diameter is not None:
            return self._diameter * (25.4 if self._units == 'imperial' else 1)
        else:
            return ValueError(f"{RED}Tool.diameter must be set (directly or indirectly) before it is referenced{ENDC}")

    @diameter.setter
    def diameter(self, value):
        self._diameter = value
        self.machine.queue(comment=f"Setting Tool Diameter: {self.diameter} mm | {self.diameter/25.4}\"", style='tool')

    @property
    def radius(self):
        return self.diameter/2

    @radius.setter
    def radius(self, value):
        self.diameter = 2*value

    @property
    def shank(self):
        if self._shank is not None:
            return self._shank
        else:
            raise ValueError(f"{RED}Tool.shank must be set (directly or indirectly) before it is referenced{ENDC}")

    @shank.setter
    def shank(self, value):
        self._shank = value
        self.machine.queue(comment=f"Setting Tool Shank: {self.shank} mm | {self.shank/25.4}\"", style='tool')

################################################################################
# Tool Length
################################################################################

    @property
    def length(self):
        if self._length is not None:
            return self._length * 25.4 if self._units == 'imperial' else self._length
        else:
            return ValueError(f"{RED}Tool.length must be set (directly or indirectly) before it is referenced{ENDC}")

    @length.setter
    def length(self, value):
        self._length = value
        self.machine.queue(comment=f"Setting Tool Length: {self.length} mm | {self.length/25.4}\"", style='tool')

    @property
    def flute_length(self):
        if self._flute_length is not None:
            return self._flute_length * 25.4 if self._units == 'imperial' else self._flute_length

    @flute_length.setter
    def flute_length(self, value):
        self._flute_length = value
        self.machine.queue(comment=f"Setting Tool Flute Length: {self.flute_length} mm | {self.flute_length/25.4}\"", style='tool')

    @property
    def max_depth(self):
        return self.flute_length if self.shank > self.diameter else self.length

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
