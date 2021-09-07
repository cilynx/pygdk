import json
import os
import sys
import math

from .tool import Tool

RED    = '\033[31m'
ORANGE = '\033[91m'
YELLOW = '\033[93m'
GREEN  = '\033[92m'
CYAN   = '\033[36m'
ENDC   = '\033[0m'

class Machine:

    MILL = 'Mill'
    LATHE = 'Lathe'

################################################################################
# Initializer -- Load details from JSON or populate from passed parameters
################################################################################

    def __init__(self, name=None, type=None, max_feed=None, safe_z=10):
        if os.path.exists(name):
            if type is not None or max_feed is not None:
                raise ValueError(f"Machine must be initialized by JSON or parameters, but not both")
            print(f";{ORANGE} Loading Machine parameters from JSON{ENDC}")
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
        self._safe_z = safe_z
        if name is None:
            self._name = type
        else:
            self._name = name
        print(f";{ORANGE} Initializing a {self.type} named {self.name}{ENDC}")

################################################################################
# Persist Machine parameters as JSON
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
        with open(file, 'w'):
            f.write(self.json + '\n')

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
                raise ValueError(f"{RED}Tool {i} is not in the Tool Table{ENDC}")
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
        print(f";{ORANGE} Setting {self.name} machine type: {value}{ENDC}")
        self._type = value

################################################################################
# Machine.name -- Only used for display, to make things more human-friendly.
################################################################################

    @property
    def name(self):
        return self._name

    @name.setter
    def name (self, value):
        print(f";{ORANGE} Renaming {self.name}: {value}{ENDC}")
        self._name = value

################################################################################
# Machine.current_tool -- Object representing the current Tool
################################################################################

    @property
    def current_tool(self):
        return self._current_tool

    @current_tool.setter
    def current_tool(self, tool):
        if isinstance(tool, int):
            self._current_tool = self.tool(tool)
        elif isinstance(tool, Tool):
            self._current_tool = tool
            tool = tool.number
        else:
            raise TypeError(f"{RED}Machine.current_tool must be set to an int or Tool object{ENDC}")
        print(f"M6 T{tool} ;{ORANGE} Select Tool {tool}{ENDC}")

    def select_tool(self, tool):
        self.current_tool = tool

################################################################################
# Machine.safe_z -- This probably belongs in a Workpiece class, not here
################################################################################

    @property
    def safe_z(self):
        return self._safe_z

    @safe_z.setter
    def safe_z(self, value):
        print(f";{ORANGE} Setting {self.name} Safe Z: {value}{ENDC}")
        self._safe_z = value

################################################################################
# Machine.max_rpm -- Used in speeds and feeds calculations.
################################################################################

    @property
    def max_rpm(self):
        return self._max_rpm

    @max_rpm.setter
    def max_rpm(self, value):
        print(f";{ORANGE} Setting {self.name} max Spindle RPM: {value}{ENDC}")
        self._max_rpm = value

################################################################################
# Machine.max_feed -- Used for rapids by default.
################################################################################

    @property
    def max_feed(self):
        return self._max_feed

    @max_feed.setter
    def max_feed(self, value):
        print(f";{ORANGE} Setting {self.name} max Feed: {value}mm/min{ENDC}")
        self._max_feed = value

################################################################################
# Machine.feed -- The current cutting feed
################################################################################

    @property
    def feed(self):
        if hasattr(self, '_feed') and self._feed is not None:
            return self._feed
        else:
            raise ValueError(f"{RED}Must set Machine.feed (directly or indirectly) prior to executing cuts")

    @feed.setter
    def feed(self, feed):
        self._feed = feed
        print(f";{YELLOW} Setting Machine Feed: {self.feed} mm/min{ENDC}")

################################################################################
# Machine.css - Constant Surface Speed
################################################################################

    @property
    def css(self):
        return self._css

    @css.setter
    def css(self, value):
        print(f";{YELLOW} Desired Constant Surface Speed (CSS): {value} m/s | {value*196.85} ft/min{ENDC}")
        if self.type == "Mill":
            print(f";{ORANGE} Calculating RPM from CSS and tool diameter.{ENDC}")
            rpm = value * 60000 / math.pi / self.current_tool.diameter
            if rpm > self.max_rpm:
                css = self.max_rpm * math.pi * self.current_tool.diameter / 60000
                print(f";{RED} {self.name} cannot do {rpm:.4f} rpm.  Maxing out at {self.max_rpm} rpm | {css:.4f} m/s | {css*196.85:.4f} ft/min{ENDC}")
                rpm = self.max_rpm;
            self.rpm = rpm

    surface_speed = css

################################################################################
# Machine.rpm - Spindle Speed
################################################################################

    @property
    def rpm(self):
        return self._rpm

    @rpm.setter
    def rpm(self, value):
        if value > self.max_rpm:
            raise ValueError(f"Tool.rpm ({value}) must be lower than Machine.max_rpm ({self.max_rpm})")
        self._rpm = value
        print(f"G97 ;{YELLOW} Constant Spindle Speed Mode{ENDC}")
        print(f";{YELLOW} Using Tool RPM: {value}{ENDC}")
        # print(f"S{value}")
        print(f";{ORANGE} Calculating CSS from RPM and tool diameter.{ENDC}")
        if self.current_tool.diameter is not None:
            self._css = self.rpm * math.pi * self.current_tool.diameter / 60000
            print(f";{YELLOW} Calculated Tool Constant Surface Speed (CSS): {self.css:.4f} m/s | {self.css*196.85:.4f} ft/min{ENDC}")
        else:
            print(f";{RED} Cannot calculate CSS from RPM because tool diameter is undefined{ENDC}")
        chip_load = 0.1 # mm/flute TODO: Parameterize this
        flutes = 4 # TODO: Parameterize this
        if chip_load is not None:
            feed = chip_load * flutes * self.rpm # mm/min
            print(f";{ORANGE} Calculated feed from chip load, flutes, and RPM: {feed:.4f} mm/min | {feed/304.8:.4f} ft/min{ENDC}")
            if feed > self.max_feed:
                print(f";{RED} {self.name} cannot feed at {feed:.4f} mm/min.  Maxing out at {self.max_feed} mm/min{ENDC}")
                feed = self.max_feed
            self.feed = feed

################################################################################
# Absolute & Incremental Movement Modes
################################################################################

    @property
    def absolute(self):
        return self._absolute

    @absolute.setter
    def absolute(self, value):
        if value not in (False,True,'0','1'):
            raise ValueError("Machine.absolute can only be set to bool (True/False) or int (0/1)")
        old_value = self._absolute if hasattr(self, '_absolute') else None
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
            raise ValueError("Machine.incremental can only be set to bool (True/False) or int (0/1)")
        self.absolute = not bool(value)

    relative = incremental

################################################################################
# Basic Linear Moves -- Rapid, iRapid, Cut, and iCut
################################################################################

    def move(self, x=None, y=None, z=None, absolute=True, cut=False, comment=None):
#        print(f";{GREEN} Cut:{cut}, X:{x}, Y:{y}, Z:{z}, ABS:{absolute}{ENDC}")
        if x is None and y is None and z is None:
            raise ValueError(f"{RED}Machine.move requires at least one coordinate to move to{ENDC}")
        self.absolute = absolute
        print("G1" if cut else "G0", end='')
        if x is not None: print(f" X{x:.4f}", end='')
        if y is not None: print(f" Y{y:.4f}", end='')
        if z is not None: print(f" Z{z:.4f}", end='')
        print(f" F{self.feed if cut else self.max_feed}", end='')
        print(f" ;{GREEN} {comment}{ENDC}" if comment else '')

    rapid = move

    def irapid(self, u=None, v=None, w=None, comment=None):
        self.move(u, v, w, absolute=False, cut=False, comment=comment)

    def cut(self, x=None, y=None, z=None, comment=None):
        self.move(x, y, z, absolute=True, cut=True, comment=comment)

    def icut(self, u=None, v=None, w=None, comment=None):
        self.move(u, v, w, absolute=False, cut=True, comment=comment)

    def retract(self, comment=None):
        self.move(z=self.safe_z, comment=comment)

################################################################################
# Machine.bolt_circle() -- Make a Bolt Circle
################################################################################

    def bolt_circle(self, c_x, c_y, n, r, depth=0):
        print(f";{CYAN} Bolt Circle | n:{n}, c:{[c_x,c_y]}, r:{r}, depth:{depth}{ENDC}")
        self.rapid(z=10, comment="Rapid to Safe Z")
        theta = 0
        delta_theta = 2*math.pi/n
        for i in range(n):
            x = c_x + (r * math.cos(theta))
            y = c_y + (r * math.sin(theta))
            self.rapid(x, y, comment=f"Rapid to {i+1}")
            self.cut(z=-10, comment=f"Drill {i+1}")
            self.rapid(z=10, comment="Retract")
            theta += delta_theta

################################################################################
# Mill Drill - Helix-drill a hole up to 2x the diameter of the end mill used
################################################################################

    def mill_drill(self, c_x, c_y, diameter, depth, z_step=0.1, retract=True):
        print(f";{CYAN} Mill Drill | center: {[c_x, c_y]}, diameter: {diameter:.4f}, depth: {depth}, z_step: {z_step:.4f}{ENDC}")
        if diameter < self.current_tool.diameter:
            raise ValueError(f"{RED}Tool {self.current_tool.number} is too big ({self.current_tool.diameter:.4f} mm) to make this small ({diameter} mm) of a pocket{ENDC}")
        if depth > self.current_tool.length:
            raise ValueError(f"{RED}Tool {self.current_tool.number} is shorter ({self.current_tool.length:.4f} mm) than pocket is deep ({depth} mm){ENDC}")
        if diameter > 2 * self.current_tool.diameter:
            raise ValueError(f"{RED}Tool {self.current_tool.number} is less than half as wide ({self.current_tool.diameter} mm) as the hole ({diameter} mm)")
        self.absolute = True
        self.rapid(z=self.safe_z, comment="Rapid to Safe Z")
        self.rapid(c_x+diameter/2-self.current_tool.diameter/2, c_y, comment="Rapid to pocket offset")
        self.rapid(z=0.1, comment="Rapid to workpiece surface")
        print(f"G17;{GREEN} Helix in XY-plane{ENDC}")
        print(f"G2 Z{-depth} I{self.current_tool.diameter/2-diameter/2:.4f} J0 P{int(depth/z_step)} F{self.feed};{GREEN} Heli-drill{ENDC}")
        print(f"G2 I{self.current_tool.diameter/2-diameter/2:.4f} J0 P1 F{self.feed};{GREEN} Clean the bottom{ENDC}")
        if retract:
            self.rapid(c_x, c_y, self.safe_z, comment="Retract")
        print(f";{CYAN} Mill Drill | END{ENDC}")

################################################################################
# Circular Pocket
################################################################################

    def circular_pocket(self, c_x, c_y, diameter, depth, step=None, finish=0.1, retract=True):
        print(f";{CYAN} Circular Pocket | center: {[c_x, c_y]}, diameter: {diameter:.4f}, depth: {depth}, step: {step}{ENDC}")
        if step is None: step = self.current_tool.diameter/10
        if diameter > 2 * self.current_tool.diameter:
            drill_diameter = 2*self.current_tool.diameter - 2*finish
        else:
            drill_diameter = diameter - 2*finish
        self.mill_drill(c_x, c_y, drill_diameter, depth, step, retract=False)
        center = self.current_tool.diameter/2-drill_diameter/2
        i = 0;
        for i in range(1, int((diameter/2-drill_diameter/2)/step)+1):
            if i%2:
                # Right to Left
                print(f"G2 I{center-i*step+step/2:.4f} X{c_x-drill_diameter/2+self.current_tool.diameter/2-i*step:.4f} F{self.feed}{'; '+GREEN+'Spiral out'+ENDC if i==1 else ''}")
            else:
                # Left to Right
                print(f"G2 I{i*step-step/2-center:.4f} X{c_x+drill_diameter/2-self.current_tool.diameter/2+i*step:.4f} F{self.feed}")
        if i%2:
            # Left to Right
            x2 = c_x+diameter/2-self.current_tool.diameter/2
            x1 = c_x+drill_diameter/2-self.current_tool.diameter/2+(i-1)*step
            print(f"G2 I{i*step-step/2-center+(x2-x1)/2:.4f} X{x2} F{self.feed}; {GREEN}Getting to final dimension{ENDC}")
            print(f"G2 I{self.current_tool.diameter/2-diameter/2} F{self.feed}; {GREEN}Final pass{ENDC}")
        else:
            # Right to Left
            x2 = c_x-diameter/2+self.current_tool.diameter/2
            x1 = c_x-drill_diameter/2+self.current_tool.diameter/2-(i-1)*step
            print(f"G2 I{center-i*step+step/2+(x2-x1)/2:.4f} X{x2} F{self.feed}; {GREEN}Getting to final dimension{ENDC}")
            print(f"G2 I{diameter/2-self.current_tool.diameter/2} F{self.feed}; {GREEN}Final pass{ENDC}")
        if retract:
            self.rapid(c_x, c_y, self.safe_z, comment="Retract")
        print(f";{CYAN} Circular Pocket | END{ENDC}")
