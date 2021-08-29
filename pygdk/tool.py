WARN  = '\033[31m' # Red
PARAM = '\033[93m' # Yellow
GREEN = '\033[92m' # Green
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
                print(f"G90 ;{GREEN} Absolute mode{ENDC}")
            else:
                print(f"G91 ;{GREEN} Incremental mode{ENDC}")

    @property
    def incremental(self):
        return not self.absolute

    @incremental.setter
    def incremental(self, value):
        if value not in (False,True,'0','1'):
            raise ValueError("Tool.incremental can only be set to bool (True/False) or int (0/1)")
        self.absolute = not bool(value)

    relative = incremental

    def move(self, x=None, y=None, z=None, absolute=True, cut=False, comment=None):
#        print(f";{GREEN} Cut:{cut}, X:{x}, Y:{y}, Z:{z}, ABS:{absolute}{ENDC}")
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
            print(f" F{self.feed if cut else self.machine.max_feed}", end='')
            if comment:
                print(f" ;{GREEN} {comment}{ENDC}")
            else:
                print()

    rapid = move

    def irapid(self, u=None, v=None, w=None, comment=None):
        print(f";{GREEN} iRapid: U:{u}, V:{v}, W:{w}{ENDC}")
        self.move(u, v, w, absolute=False, cut=False, comment=comment)

    def cut(self, x=None, y=None, z=None, comment=None):
        self.move(x, y, z, absolute=True, cut=True, comment=comment)

    def icut(self, u=None, v=None, w=None, comment=None):
        self.move(u, v, w, absolute=False, cut=True, comment=comment)

    def bolt_circle(self, n, c_x, c_y, r, depth=0):
        self.rapid(z=10)
        theta = 0
        delta_theta = 2*math.pi/n
        print(f";{GREEN} Bolt Circle | n:{n}, c:{[c_x,c_y]}, r:{r}, depth:{depth}{ENDC}")
        for i in range(n):
            x = c_x + (r * math.cos(theta))
            y = c_y + (r * math.sin(theta))
            self.rapid(x, y)
            self.cut(z=-10, comment="Drill")
            self.rapid(z=10, comment="Retract")
            theta += delta_theta
