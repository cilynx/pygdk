WARN  = '\033[31m' # Red
PARAM = '\033[93m' # Yellow
RAPID = '\033[92m' # Green
ENDC  = '\033[0m'  # End Color
MACHINE = '\033[91m' # Orange

import math

class Tool:
    def __init__(self, machine):
        self._machine   = machine
        self._absolute  = None
        self._diameter  = None
        self._metric    = True
        self._rpm       = None
        self._css       = None
        self._material  = None
        self._feed      = None

    @property
    def machine(self):
        return self._machine

    @property
    def diameter(self):
        return self._diameter

    @diameter.setter
    def diameter(self, value):
        self._diameter = value
        print(f";{PARAM} Setting Tool Diameter: {self.diameter}mm ({self.diameter/25.4}\"){ENDC}")

    @property
    def feed(self):
        return self._feed

    @feed.setter
    def feed(self, value):
        self._feed = value
        print(f";{PARAM} Setting Tool Feed: {self.feed}mm/min{ENDC}")

    @property
    def css(self):
        return self._css

    @css.setter
    def css(self, value):
        print(f";{PARAM} Desired Tool Constant Surface Speed (CSS): {value}m/s{ENDC}")
        if self.machine.type == "Mill":
            print(f";{MACHINE} Calculating RPM from CSS and tool diameter.{ENDC}")
            if self.diameter is not None:
                rpm = value * 60000 / math.pi / self.diameter
                if rpm > self.machine.max_rpm:
                    raise ValueError(f"Tool.rpm ({rpm}) must be lower than Machine.max_rpm ({self.machine.max_rpm})")
                self.rpm = rpm
            else:
                raise ValueError(f"{WARN}Cannot calculate RPM from CSS because tool diameter is undefined{ENDC}")

    surface_speed = css

    @property
    def rpm(self):
        return self._rpm

    @rpm.setter
    def rpm(self, value):
        if value > self.machine.max_rpm:
            raise ValueError(f"Tool.rpm ({value}) must be lower than Machine.max_rpm ({self.machine.max_rpm})")
        self._rpm = value
        print(f";{PARAM} Setting Constant Spindle Speed Mode{ENDC}")
        print("G97")
        print(f";{PARAM} Setting Tool RPM: {value}{ENDC}")
        print(f"S{value}")
        print(f";{MACHINE} Calculating CSS from RPM and tool diameter.{ENDC}")
        if self.diameter is not None:
            self._css = self.rpm * math.pi * self.diameter / 60000
            print(f";{PARAM} Calculated Tool Constant Surface Speed (CSS): {self.css}m/s{ENDC}")
        else:
            print(f";{WARN} Cannot calculate CSS from RPM because tool diameter is undefined{ENDC}")


    @property
    def absolute(self):
        return self._absolute

    @absolute.setter
    def absolute(self, value):
        if value not in (False,True,'0','1'):
            raise ValueError("Tool.absolute can only be set to bool (True/False) or int (0/1)")
        old_value = self._absolute
        self._absolute = bool(value)
        if self._absolute != old_value:
            if self._absolute:
                print("G90")
            else:
                print("G91")

    @property
    def incremental(self):
        return not self.absolute

    @incremental.setter
    def incremental(self, value):
        if value not in (False,True,'0','1'):
            raise ValueError("Tool.incremental can only be set to bool (True/False) or int (0/1)")
        self.absolute = not bool(value)

    relative = incremental

    def move(self, x=None, y=None, z=None, absolute=True, cut=False):
        print(f";{RAPID} Cut:{cut}, X:{x}, Y:{y}, Z:{z}, ABS:{absolute}{ENDC}")
        if x is None and y is None and z is None:
            raise ValueError(f"{WARN}Tool.move requires at least one coordinate to move to{ENDC}")
        else:
            self.absolute = absolute
            print("G1" if cut else "G0", end='')
            if x is not None:
                print(f" X{x}", end='')
            if y is not None:
                print(f" Y{y}", end='')
            if z is not None:
                print(f" Z{z}", end='')
            print(f" F{self.feed if cut else self.machine.max_feed}")

    rapid = move

    def irapid(self, u=None, v=None, w=None):
        print(f";{RAPID} iRapid: U:{u}, V:{v}, W:{w}{ENDC}")
        self.move(u, v, w, absolute=False)

    def cut(self, x=None, y=None, z=None):
        self.move(x, y, z, absolute=True, cut=True)

    def icut(self, u=None, v=None, w=None):
        self.move(u, v, w, absolute=False, cut=True)

    def bolt_circle(self, count, c_x, c_y, radius, depth=0):
        self.rapid(z=10)
        theta = 0
        delta_theta = 2*math.pi/count
        for i in range(count):
            x = c_x + (radius * math.cos(theta))
            y = c_y + (radius * math.sin(theta))
            self.rapid(x, y)
            self.cut(z=0)
            self.rapid(z=10)
            theta += delta_theta
