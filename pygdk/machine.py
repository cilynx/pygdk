import json
import os
import sys
import math

from .tool import Tool
from .turtle import Turtle

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
            print(f";{YELLOW} Loading Machine parameters from JSON{ENDC}")
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
                if 'Plotter' in dict:
                    self._plotter = dict['Plotter']
                else:
                    self._plotter = None
        if not type in [self.MILL, self.LATHE]:
            raise ValueError(f"Machine type ({type}) must be Machine.MILL or Machine.LATHE")
        self._type = type
        self._max_feed = max_feed
        self._safe_z = safe_z
        if name is None:
            self._name = type
        else:
            self._name = name
        self._x_offset = 0
        self._y_offset = 0
        self._z_offset = 0
        self._current_tool = None
        self._absolute = None
        self._feed = None
        self._turtle = None
        self._optimize = False
        self._x = 0
        self._y = 0
        self._z = 0
        self._linear_moves = {None:[]}
        self._optimize_tool = None
        self._material = None
        self._x_clear = None
        self._y_clear = None
        self._z_clear = None
        print(f";{YELLOW} Initializing a {self.type} named {self.name}{ENDC}")

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
                for index in self._tool_table:
                    if i in self._tool_table[str(index)]['description']:
                        return Tool(self, self._tool_table[str(index)], str(index))
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
        print(f";{YELLOW} Setting {self.name} machine type: {value}{ENDC}")
        self._type = value

################################################################################
# Machine.name -- Only used for display, to make things more human-friendly.
################################################################################

    @property
    def name(self):
        return self._name

    @name.setter
    def name (self, value):
        print(f";{YELLOW} Renaming {self.name}: {value}{ENDC}")
        self._name = value

################################################################################
# Tool Offsets -- Mostly for the Plotter
################################################################################

    @property
    def x_offset(self):
        return self._x_offset

    @x_offset.setter
    def x_offset (self, value):
        print(f";{YELLOW} Setting x_offset: {value}{ENDC}")
        self._x_offset = value

    @property
    def y_offset(self):
        return self._y_offset

    @y_offset.setter
    def y_offset (self, value):
        print(f";{YELLOW} Setting y_offset: {value}{ENDC}")
        self._y_offset = value

    @property
    def z_offset(self):
        return self._z_offset

    @z_offset.setter
    def z_offset (self, value):
        print(f";{YELLOW} Setting z_offset: {value}{ENDC}")
        self._z_offset = value

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
        elif isinstance(tool, str):
            self._current_tool = self.tool(tool)
            tool = self._current_tool.number
        elif isinstance(tool, Tool):
            self._current_tool = tool
            tool = self._current_tool.number
        else:
            raise TypeError(f"{RED}Machine.current_tool must be set to an int (Tool Number), str (Tool Description), or Tool object{ENDC}")
        if 'Sharpie' not in self.current_tool._description or self._simulate:
            position = [self._x, self._y, self._z]
            self.rapid(z=0, machine_coord=True, comment="Fully retracting")
            if self._y_clear is not None:
                self.rapid(y=self._y_clear, comment="Clearing to _y_clear")
            self.rapid(x=0, machine_coord=True, comment="Zeroing left")
            self.rapid(y=0, machine_coord=True, comment="Zeroing forward")
            self.pause(self.current_tool._description)
            if self._y_clear is not None:
                self.rapid(y=self._y_clear)
            self.rapid(x=position[0])
            self.rapid(y=position[1])
#            self.rapid(z=-10, machine_coord=True)
            print(f"M6 T{tool} ;{GREEN} Select Tool {tool}{ENDC}")
        else:
            print(f";{YELLOW} Select Tool {tool}{ENDC}")
        if self.material:
            self.update_fas()

    def select_tool(self, tool):
        self.current_tool = tool

################################################################################
# Machine.material -- Workpiece material.  Still thinking about a separate class
################################################################################

    @property
    def material(self):
        return self._material

    @material.setter
    def material(self,value):
        self._material = value
        if self.current_tool:
            self.update_fas()

################################################################################
# Feeds and Speeds
################################################################################

    def update_fas(self):
        if self.material and self.current_tool:
            fas_file = 'feeds-and-speeds.json'
            if os.path.exists(fas_file):
                with open(fas_file, 'r') as fas:
                    self._fas = json.load(fas)
            sfm = self._fas['SFM']
            chipload = self._fas['Chipload']
            cutter = self.current_tool.material
            if self.material in sfm[cutter] and self.material in chipload:
                print(f";{YELLOW} Workpiece is {self.material}{ENDC}")

                if self.current_tool.rpm:
                    rpm = (self.current_tool.rpm[self.material][0]+self.current_tool.rpm[self.material][1])/2
                    print(f";{YELLOW} Using tool manufacturer recommended spindle RPM: {rpm:.4f} rpm{ENDC}")
                    self.rpm = rpm
                else:
                    self.css = (sfm[cutter][self.material][0]+sfm[cutter][self.material][1])/2/196.85

                if self.current_tool.ipm:
                    ipm = (self.current_tool.ipm[self.material][0]+self.current_tool.ipm[self.material][1])/2
                    print(f";{YELLOW} Using tool manufacturer recommended feed: {ipm:.4f} in/min{ENDC}")
                    self.feed = ipm*25.4
                else:
                    print(f";{YELLOW} No manufacturer-recommended IPM Feed.  Calculating.{ENDC}")
                    cl_range = chipload[self.material].get(f"{self.current_tool.diameter/25.4:.3f}", None)
                    if cl_range:
                        cl_mean = (cl_range[0]+cl_range[1])/2
                        self.feed = self.rpm * self.current_tool.flutes * cl_mean * 25.4
                    else:
                        print(f";{RED} Tool not available in chipload table.  You're on your own for feeds and speeds.{ENDC}")

################################################################################
# Machine.safe_z -- This probably belongs in a Workpiece class, not here
################################################################################

    @property
    def safe_z(self):
        return self._safe_z

    @safe_z.setter
    def safe_z(self, value):
        print(f";{YELLOW} Setting {self.name} Safe Z: {value}{ENDC}")
        self._safe_z = value

################################################################################
# Machine.max_rpm -- Used in speeds and feeds calculations.
################################################################################

    @property
    def max_rpm(self):
        return self._max_rpm

    @max_rpm.setter
    def max_rpm(self, value):
        print(f";{YELLOW} Setting {self.name} max Spindle RPM: {value}{ENDC}")
        self._max_rpm = value

################################################################################
# Machine.max_feed -- Used for rapids by default.
################################################################################

    @property
    def max_feed(self):
        return self._max_feed

    @max_feed.setter
    def max_feed(self, value):
        print(f";{YELLOW} Setting {self.name} max Feed: {value}mm/min{ENDC}")
        self._max_feed = value

################################################################################
# Machine.feed -- The current cutting feed
################################################################################

    @property
    def feed(self):
        if self._feed is not None:
            return self._feed
        else:
            raise ValueError(f"{RED}Must set Machine.feed (directly or indirectly) prior to executing cuts")

    @feed.setter
    def feed(self, feed):
        self._feed = feed
        print(f";{YELLOW} Using Machine Feed: {self.feed:.4f} mm/min | {self.feed/25.4:.4f} in/min | {self.feed/25.4/12:.4f} ft/min{ENDC}")

################################################################################
# Machine.css - Constant Surface Speed
################################################################################

    @property
    def css(self):
        return self._css

    @css.setter
    def css(self, value):
        print(f";{YELLOW} Desired Constant Surface Speed (CSS): {value:.4f} m/s | {value*196.85:.4f} ft/min{ENDC}")
        if self.type == "Mill":
            print(f";{YELLOW} Calculating RPM from CSS and tool diameter.")
            rpm = value * 60000 / math.pi / self.current_tool.diameter
            if rpm > self.max_rpm:
                css = self.max_rpm * math.pi * self.current_tool.diameter / 60000
                print(f";{RED} {self.name} cannot do {rpm:.4f} rpm.  Maxing out at {self.max_rpm} rpm | {css:.4f} m/s | {css*196.85:.4f} ft/min{ENDC}")
                rpm = self.max_rpm;
            print(f";{YELLOW} Setting RPM: {rpm:.4f}{ENDC}")
            self._rpm = rpm

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
            raise ValueError(f"Machine.rpm ({value}) must be lower than Machine.max_rpm ({self.max_rpm})")
        self._rpm = value
        print(f"G97 ;{GREEN} Constant Spindle Speed Mode{ENDC}")
        print(f"S{value:.4f} ;{GREEN} Using Spindle RPM: {value:.4f}{ENDC}")
        # print(f"S{value}")
        print(f";{YELLOW} Calculating CSS from RPM and tool diameter.{ENDC}")
        if self.current_tool.diameter is not None:
            self._css = self.rpm * math.pi * self.current_tool.diameter / 60000
            print(f";{YELLOW} Calculated Tool Constant Surface Speed (CSS): {self.css:.4f} m/s | {self.css*196.85:.4f} ft/min{ENDC}")
        else:
            print(f";{RED} Cannot calculate CSS from RPM because tool diameter is undefined{ENDC}")
        chip_load = 0.1 # mm/flute TODO: Parameterize this
        flutes = 4 # TODO: Parameterize this
        if chip_load is not None:
            feed = chip_load * flutes * self.rpm # mm/min
            print(f";{YELLOW} Calculated feed from chip load, flutes, and RPM: {feed:.4f} mm/min | {feed/304.8:.4f} ft/min{ENDC}")
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
            raise ValueError("Machine.incremental can only be set to bool (True/False) or int (0/1)")
        self.absolute = not bool(value)

    relative = incremental

################################################################################
# Linear Moves -- Rapid, iRapid, Cut, and iCut
################################################################################

    def move(self, x=None, y=None, z=None, absolute=True, machine_coord=False, cut=False, comment=None):
#        print(f";{GREEN} Cut:{cut}, X:{x}, Y:{y}, Z:{z}, ABS:{absolute}{ENDC}")
        if x is not None:
            x = x+self.x_offset
        if y is not None:
            y = y+self.y_offset
        if z is not None:
            z = z+self.z_offset

        if x is None and y is None and z is None:
            raise ValueError(f"{RED}Machine.move requires at least one coordinate to move to{ENDC}")
        self.absolute = absolute
        if self.absolute and self._optimize:
#            print(self._optimize_tool)
#            print([[self._x, self._y, self._z],[x,y,z]])
            old_pos = [None, None, None]
            new_pos = [None, None, None]

            old_pos[0] = self._x
            new_pos[0] = x if x is not None else self._x
            if x is not None:
                self._x = x

            old_pos[1] = self._y
            new_pos[1] = y if y is not None else self._y
            if y is not None:
                self._y = y

            old_pos[2] = self._z
            new_pos[2] = z if z is not None else self._z
            if z is not None:
                self._z = z

            self._linear_moves[self._optimize_tool].append([old_pos, new_pos])
        elif self._optimize:
            raise NotImplementedError(f"{RED}Optimizing relative moves is not yet implemented")
        else:
            G = 'G53 G' if machine_coord else 'G'
            print(f"{G}1" if cut else f"{G}0", end='')
            if x is not None:
                print(f" X{x:.4f}", end='')
                self._x = x
            if y is not None:
                print(f" Y{y:.4f}", end='')
                self._y = y
            if z is not None:
                print(f" Z{z:.4f}", end='')
                self._z = z
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

    def full_retract(self, comment=None):
        self.move(z=0, machine_coord=True, comment=comment)

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
            self.cut(z=depth, comment=f"Drill {i+1}")
            self.rapid(z=10, comment="Retract")
            theta += delta_theta
        print(f";{CYAN} Bolt Circle | END{ENDC}")

################################################################################
# Mill Drill - Helix-drill a hole up to 2x the diameter of the end mill used
################################################################################

    def mill_drill(self, c_x, c_y, diameter, depth, z_step=0.1, outside=False, retract=True):
        print(f";{CYAN} Mill Drill | center: {['{:.4f}'.format(c_x), '{:.4f}'.format(c_y)]}, diameter: {diameter:.4f}, depth: {depth}, z_step: {z_step:.4f}{ENDC}")
        if diameter > 2 * self.current_tool.diameter:
            raise ValueError(f"{RED}Tool {self.current_tool.number} ({self.current_tool.diameter:.4f} mm) is less than half as wide as the hole ({diameter} mm).  Use a larger endmill or make a pocket instead of mill-drilling.")
        self.helix(c_x, c_y, diameter, depth, z_step, outside, retract)
        print(f";{CYAN} Mill Drill | END{ENDC}")

################################################################################
# Helix - Helix-mill a circle with the cutter on either the inside (default)
#         or outside of the requested diameter
################################################################################

    def helix(self, c_x, c_y, diameter, depth, z_step=0.1, outside=False, retract=True):
        if self._optimize:
            raise ValueError(f"{RED}The _optimize option currently does not work with helix operations")
        print(f";{CYAN} Helix | center: {['{:.4f}'.format(c_x), '{:.4f}'.format(c_y)]}, diameter: {diameter:.4f}, depth: {depth}, z_step: {z_step:.4f}{ENDC}")
        if diameter < self.current_tool.diameter:
            raise ValueError(f"{RED}Tool {self.current_tool.number} is too big ({self.current_tool.diameter:.4f} mm) to make this small ({diameter} mm) of a hole{ENDC}")
        if depth > self.current_tool.length:
            raise ValueError(f"{RED}Tool {self.current_tool.number} is shorter ({self.current_tool.length:.4f} mm) than the cut is deep ({depth} mm){ENDC}")
        if z_step > depth:
            raise ValueError(f"{RED}z_step cannot be greater than depth{ENDC}")
        if outside:
            diameter = -diameter
        self.absolute = True
        self.rapid(z=self.safe_z, comment="Rapid to Safe Z")
        self.rapid(c_x+diameter/2-self.current_tool.diameter/2, c_y, comment="Rapid to pocket offset")
        self.rapid(z=0.1, comment="Rapid to workpiece surface")
        print(f"G17;{GREEN} Helix in XY-plane{ENDC}")
        print(f"G2 Z{-depth} I{self.current_tool.diameter/2-diameter/2:.4f} J0 P{int(depth/z_step)} F{self.feed};{GREEN} Heli-drill{ENDC}")
        print(f"G2 I{self.current_tool.diameter/2-diameter/2:.4f} J0 P1 F{self.feed};{GREEN} Clean the bottom{ENDC}")
        if retract:
            self.rapid(z=self.safe_z, comment="Retract")
            self.rapid(c_x, c_y, comment="Re-Center")
        print(f";{CYAN} Helix | END{ENDC}")

    circle = helix

################################################################################
# Circular Pocket
################################################################################

    def circular_pocket(self, c_x, c_y, diameter, depth, step=None, finish=0.1, retract=True):
        print(f";{CYAN} Circular Pocket | center: {['{:.4f}'.format(c_x), '{:.4f}'.format(c_y)]}, diameter: {diameter:.4f}, depth: {depth}, step: {step}, finish: {finish}{ENDC}")
        if self._optimize:
            raise ValueError(f"{RED}The _optimize option currently does not work with circular operations")
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

################################################################################
# Machine.pocket_circle() -- Like a Bolt Circle, but with Circular Pockets
################################################################################

    def pocket_circle(self, c_x, c_y, n, r, depth, diameter, step=None, finish=0.1):
        print(f";{CYAN} Pocket Circle | n:{n}, c:{[c_x,c_y]}, r:{r}, depth:{depth}, diameter:{diameter}, step:{step}, finish:{finish}{ENDC}")
        self.rapid(z=10, comment="Rapid to Safe Z")
        theta = 0
        delta_theta = 2*math.pi/n
        for i in range(n):
            x = c_x + (r * math.cos(theta))
            y = c_y + (r * math.sin(theta))
            self.circular_pocket(x, y, diameter, depth, step, finish)
            theta += delta_theta
        print(f";{CYAN} Pocket Circle | END{ENDC}")

################################################################################
# Rectangular Frame
################################################################################

    def frame(self, c_x, c_y, x, y, depth, z_step=None, outside=True, retract=True, c='center', r=None, r_steps=10, feature=None):
        if feature:
            print(f";{ORANGE} {feature}{ENDC}")
        print(f";{CYAN} Rectangular Frame | [c_x,c_y]: {['{:.4f}'.format(c_x), '{:.4f}'.format(c_y)]}, x: {x:.4f}, y: {y:.4f}, depth: {depth}, z_step: {z_step}, outside: {outside}, c: {c}, r: {r}{ENDC}")

        if r is None:
            r = 0 if outside else self.current_tool.radius
        if not outside and r < self.current_tool.radius:
            raise ValueError(f"{RED}Tool radius ({self.current_tool.radius} mm) is larger than requested inside corner radius ({r} mm)")

        if not self.current_tool:
            raise ValueError(f"{RED}You can't cut a frame without selecting a tool first")
        if depth > self.current_tool.length:
            raise ValueError(f"{RED}Tool {self.current_tool.number} is shorter ({self.current_tool.length:.4f} mm) than frame is deep ({depth} mm){ENDC}")

        if not z_step:
            z_step = self.current_tool.diameter
        if z_step > depth:
            z_step = depth
        passes = math.ceil(depth/z_step)
        z_step = depth/passes

        flx = c_x
        fly = c_y
        if c.lower() == 'center':
            flx = c_x-x/2
            fly = c_y-y/2
        elif c.lower() == 'fr':
            flx = c_x-x
        elif c.lower() == 'rl':
            fly = c_y+y
        elif c.lower() == 'rr':
            flx = c_x-x
            fly = c_y+y
        elif c is not None and c.lower() != 'fl':
            raise ValueError(f"{RED}Corner must be 'FL','FR','RL','RR', or 'Center'{ENDC}")

        tool_d = self.current_tool.diameter if outside else -self.current_tool.diameter

        turtle = self.turtle(verbose=True)
        turtle.penup()
        turtle.goto(flx+r, fly-tool_d/2, comment="Rapid to front-left corner:")
        turtle.pendown()
        for i in range(passes+1):
            if i == passes:
                z_step = 0
            turtle.forward(x-2*r, -z_step/4)
            turtle.circle(radius=r+tool_d/2, extent=90, steps=r_steps) # TODO: Implement smooth Turtle circles and drop the steps here
            turtle.forward(y-2*r, -z_step/4)
            turtle.circle(radius=r+tool_d/2, extent=90, steps=r_steps)
            turtle.forward(x-2*r, -z_step/4)
            turtle.circle(radius=r+tool_d/2, extent=90, steps=r_steps)
            turtle.forward(y-2*r, -z_step/4)
            turtle.circle(radius=r+tool_d/2, extent=90, steps=r_steps)

        self.retract()
        print(f";{CYAN} End Rectangular Frame{ENDC}")

    rectangle = frame

################################################################################
# Rectangular Pocket
################################################################################

    def rectangular_pocket(self, c_x, c_y, x, y, depth, step=None, finish=0.1, undercut=False, retract=True):
        print(f";{CYAN} Rectangular Pocket | center: {['{:.4f}'.format(c_x), '{:.4f}'.format(c_y)]}, x: {x:.4f}, y: {y:.4f}, depth: {depth}, step: {step}, finish: {finish}, undercut: {undercut}{ENDC}")
        if not self.current_tool:
            raise ValueError(f"{RED}You can't cut a pocket without selecting a tool first")
        if depth > self.current_tool.length:
            raise ValueError(f"{RED}Tool {self.current_tool.number} is shorter ({self.current_tool.length:.4f} mm) than pocket is deep ({depth} mm){ENDC}")
        rough_depth = depth#-2*finish
        rough_x = x-2*finish
        rough_y = y-2*finish
        short = min(rough_x,rough_y)
        if short < self.current_tool.diameter:
            raise ValueError(f"{RED}Tool {self.current_tool.number} is too big ({self.current_tool.diameter:.4f} mm) to make this small ({short} mm) of a pocket{ENDC}")
        if step is None: step = self.current_tool.diameter/10

        # Ramp down to rough depth in the center, equidistant to each edge
        ramp_short = min(short-self.current_tool.diameter, 3/4*self.current_tool.diameter)
        long = max(rough_x,rough_y)
        ramp_long = ramp_short + long - short
        ramp_x = ramp_long if x > y else ramp_short
        ramp_y = ramp_long if y > x else ramp_short
        ramp_passes = 4*math.ceil(rough_depth/step/4)
        ramp_step = rough_depth / ramp_passes
        assert ramp_step <= step
        spiral_passes = 2*math.ceil((rough_x-ramp_x-self.current_tool.diameter)/step/2)
        if spiral_passes == 0:
            spiral_passes = 1
        spiral_step = (rough_x-ramp_x-self.current_tool.diameter)/spiral_passes
        assert spiral_step <= step
        self.retract(comment="Retract")
        for i in range(0,int(ramp_passes/4)):
            self.cut(c_x-ramp_x/2, c_y+ramp_y/2, -(4*i+0)*ramp_step, comment = f"Ramp pass {i+1}")
            self.cut(c_x+ramp_x/2, c_y+ramp_y/2, -(4*i+1)*ramp_step)
            self.cut(c_x+ramp_x/2, c_y-ramp_y/2, -(4*i+2)*ramp_step)
            self.cut(c_x-ramp_x/2, c_y-ramp_y/2, -(4*i+3)*ramp_step)
        self.cut(c_x-ramp_x/2, c_y+ramp_y/2, -rough_depth, comment = f"Ramp pass {i+2}")
        self.cut(c_x+ramp_x/2, c_y+ramp_y/2, -rough_depth)
        self.cut(c_x+ramp_x/2, c_y-ramp_y/2, -rough_depth)
        self.cut(c_x-ramp_x/2, c_y-ramp_y/2, -rough_depth)
        self.cut(c_x-ramp_x/2, c_y+ramp_y/2, -rough_depth)

        # Spiral out to dimension-finish
        for i in range(0,int(spiral_passes/2)):
            self.cut(c_x-ramp_x/2-i*spiral_step, c_y+ramp_y/2+i*spiral_step, comment=f"Spiral pass {i+1}")
            self.cut(c_x+ramp_x/2+i*spiral_step, c_y+ramp_y/2+i*spiral_step)
            self.cut(c_x+ramp_x/2+i*spiral_step, c_y-ramp_y/2-i*spiral_step)
            self.cut(c_x-ramp_x/2-(i+1)*spiral_step, c_y-ramp_y/2-i*spiral_step)

        # On final pass, ramp to final dimension (x,y,z) in one corner, then finish all four sides.
        # Add undercuts on each corner if needed
        d = self.current_tool.diameter
        h = d*math.sqrt(2)
        s = 1/2*(h-d)
        corner = math.sqrt((s**2)/2)

        self.cut(c_x-x/2+d/2, c_y+y/2-d/2, comment="Finishing pass")
        self.cut(c_x+x/2-d/2, c_y+y/2-d/2)
        if undercut:
            self.cut(c_x+x/2-d/2+corner, c_y+y/2-d/2+corner, comment="Top Left Undercut")
            self.cut(c_x+x/2-d/2, c_y+y/2-d/2)
        self.cut(c_x+x/2-d/2, c_y-y/2+d/2)
        if undercut:
            self.cut(c_x+x/2-d/2+corner, c_y-y/2+d/2-corner, comment="Top Right Undercut")
            self.cut(c_x+x/2-d/2, c_y-y/2+d/2)
        self.cut(c_x-x/2+d/2, c_y-y/2+d/2)
        if undercut:
            self.cut(c_x-x/2+d/2-corner, c_y-y/2+d/2-corner, comment="Bottom Right Undercut")
            self.cut(c_x-x/2+d/2, c_y-y/2+d/2)
        self.cut(c_x-x/2+d/2, c_y+y/2-d/2)
        if undercut:
            self.cut(c_x-x/2+d/2-corner, c_y+y/2-d/2+corner, comment="Bottom Left Undercut")
            self.cut(c_x-x/2+d/2, c_y+y/2-d/2)
        if retract:
            self.rapid(c_x, c_y, self.safe_z, comment="Retract")

        print(f";{CYAN} Rectangular Pocket | END{ENDC}")

################################################################################
# Pen Color
################################################################################

    @property
    def pen_color(self):
        return self.current_tool._description

    @pen_color.setter
    def pen_color(self, value):
        if not self._plotter:
            raise ValueError(f"{RED}You must configure a Plotter before you can set pen_color{ENDC}")

        if self._optimize:
            if value is None:
#                print(json.dumps(self._linear_moves, indent=4))
                self._optimize = False
                for color in self._linear_moves:
                    if color:
                        self.pen_color = color
                        for move in self._linear_moves[color]:
                            self.rapid(move[0][0], move[0][1], move[0][2], comment="Rapid to next start")
                            self.cut(move[1][0], move[1][1], move[1][2], comment="Execute move")
            elif any(value in row for row in self._plotter['Magazine']):
                self._linear_moves.setdefault(value,[])
                self._optimize_tool = value
            else:
                raise ValueError(f"{RED}'{value}' is not a configured color.  Options are: {self._plotter['Magazine']}" )

        else:
            self.rapid(z=self._plotter['Z-Stage'], comment="Go to pen change staging height")
            if self.current_tool:
                self.rapid(x=self._plotter['Slot Zero'][0], y=self._plotter['Slot Zero'][1], z=self._plotter['Z-Stage'], comment="Stage to retract current pen")
                self.rapid(z=self._plotter['Z-Click'], comment="Retract current pen")
                self.rapid(z=self._plotter['Z-Stage'], comment="Return to pen change stage")
            if value is None:
                self.x_offset = 0;
                self.y_offset = 0;
                rows = len(self._plotter['Magazine'])
                backset = self._plotter['Slot Zero'][1] + (rows+1)*self._plotter['Pen Spacing'];
                self.rapid(x=self._plotter['Slot Zero'][0], y=backset, comment="Rapid to homing-safe backset")
                return self.current_tool
            for row in self._plotter['Magazine']:
                if value in row:
                    i = row.index(value)
                    j = self._plotter['Magazine'].index(row)
                    self.x_offset = -i*self._plotter['Pen Spacing']
                    self.y_offset = j*self._plotter['Pen Spacing']
                    self.rapid(x=self._plotter['Slot Zero'][0], y=self._plotter['Slot Zero'][1], z=self._plotter['Z-Stage'], comment="Stage to activate new pen")
                    self.rapid(z=self._plotter['Z-Click'], comment="Activate new pen")
                    self.rapid(z=self._plotter['Z-Stage'], comment="Return to pen change stage")
                    self.current_tool = value
                    return self.current_tool
            raise ValueError(f"{RED}'{value}' is not a configured color.  Options are: {self._plotter['Magazine']}" )

################################################################################
# Turtle Object Reference
################################################################################

    def turtle(self, x=0, y=0, z=0, z_draw=0, mode='standard', verbose=False):
        return Turtle(self, x, y, z, z_draw, mode, verbose)

################################################################################
# Modal State -- M70, M71, M72
################################################################################

    def save_modal_state(self):
        print(f"M70 ;{GREEN} Save Modal State")

    def invalidate_modal_state(self):
        print(f"M71 ;{GREEN} Invalidate Modal State")

    def restore_modal_state(self):
        print(f"M72 ;{GREEN} Restore Modal State")

################################################################################
# Modal State -- M70, M71, M72
################################################################################

    def pause(self, msg="Paused, Click Done to resume"):
        print(f"M0 (MSG, {msg})")
