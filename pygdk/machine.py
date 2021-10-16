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
    FDM_PRINTER = 'FDM Printer'

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
        if not type in [self.MILL, self.LATHE, self.FDM_PRINTER]:
            raise ValueError(f"Machine type ({type}) must be Machine.MILL, Machine.LATHE, or Machine.FDM_PRINTER")
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
        self._tool = None
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

    def tool_from_tool_table(self, i):
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
# Machine.tool -- Object representing the current Tool
################################################################################

    @property
    def tool(self):
        return self._tool

    @tool.setter
    def tool(self, tool):
        previous_tool = self.tool
        if isinstance(tool, int):
            self._tool = self.tool_from_tool_table(tool)
        elif isinstance(tool, str):
            self._tool = self.tool_from_tool_table(tool)
            tool = self._tool.number
        elif isinstance(tool, Tool):
            self._tool = tool
            tool = self._tool.number
        else:
            raise TypeError(f"{RED}Machine.tool must be set to an int (Tool Number), str (Tool Description), or Tool object{ENDC}")
        if 'Sharpie' not in self.tool._description or self._simulate:
            if previous_tool is None:
                print(f";{CYAN} Assuming first tool is already loaded{ENDC}")
            else:
                print(f";{CYAN} Coming around for Tool Change{ENDC}")
                position = [self._x, self._y, self._z]
                self.full_retract()
                if self._y_clear is not None:
                    self.rapid(y=self._y_clear, comment="Clearing to _y_clear")
                self.rapid(x=0, machine_coord=True, comment="Zero left")
                self.rapid(y=0, machine_coord=True, comment="Zero forward")
                self.pause(self.tool._description)
                if self._y_clear is not None:
                    self.rapid(y=self._y_clear)
                self.rapid(x=position[0])
                self.rapid(y=position[1])
    #            self.rapid(z=-10, machine_coord=True)
            print(f"M6 T{tool} ;{GREEN} Select Tool {tool}{ENDC}")
        else:
            print(f";{YELLOW} Select Tool {tool}{ENDC}")
        print(f";{CYAN} End Tool Change{ENDC}")
        if self.material:
            self.update_fas()

################################################################################
# Machine.material -- Workpiece material.  Still thinking about a separate class
################################################################################

    @property
    def material(self):
        return self._material

    @material.setter
    def material(self,value):
        self._material = value
        if self.tool:
            self.update_fas()
        return self.material

################################################################################
# Feeds and Speeds
################################################################################

    def update_fas(self):
        if self.material and self.tool:
            fas_file = 'feeds-and-speeds.json'
            if os.path.exists(fas_file):
                with open(fas_file, 'r') as fas:
                    self._fas = json.load(fas)
            sfm = self._fas['SFM']
            chipload = self._fas['Chipload']
            cutter = self.tool.material
            if self.material in sfm[cutter] and self.material in chipload:
                print(f";{YELLOW} Workpiece is {self.material}{ENDC}")

                if self.tool.rpm:
                    rpm = (self.tool.rpm[self.material][0]+self.tool.rpm[self.material][1])/2
                    print(f";{YELLOW} Using tool manufacturer recommended spindle RPM: {rpm:.4f} rpm{ENDC}")
                    self.rpm = rpm
                else:
                    self.css = (sfm[cutter][self.material][0]+sfm[cutter][self.material][1])/2/196.85

                if self.tool.ipm:
                    ipm = (self.tool.ipm[self.material][0]+self.tool.ipm[self.material][1])/2
                    print(f";{YELLOW} Using tool manufacturer recommended feed: {ipm:.4f} in/min{ENDC}")
                    self.feed = ipm*25.4
                else:
                    print(f";{YELLOW} No manufacturer-recommended IPM Feed.  Calculating.{ENDC}")
                    cl_range = chipload[self.material].get(f"{self.tool.diameter/25.4:.3f}", None)
                    if cl_range:
                        cl_mean = (cl_range[0]+cl_range[1])/2
                        self.feed = self.rpm * self.tool.flutes * cl_mean * 25.4
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
            print(f";{YELLOW} Calculating RPM from CSS and tool diameter.{ENDC}")
            rpm = value * 60000 / math.pi / self.tool.diameter
            if rpm > self.max_rpm:
                css = self.max_rpm * math.pi * self.tool.diameter / 60000
                print(f";{RED} {self.name} cannot do {rpm:.4f} rpm.  Maxing out at {self.max_rpm} rpm | {css:.4f} m/s | {css*196.85:.4f} ft/min{ENDC}")
                rpm = self.max_rpm;
            print(f";{YELLOW} Setting RPM: {rpm:.4f} | {rpm/60:.4f} Hz on the VFD{ENDC}")
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
        print(f"G97 ;{GREEN} Constant Spindle Speed{ENDC}")
        print(f"S{value:.4f} ;{GREEN} Set Spindle RPM: {value:.4f}{ENDC}")
        # print(f"S{value}")
        print(f";{YELLOW} Calculating CSS from RPM and tool diameter.{ENDC}")
        if self.tool.diameter is not None:
            self._css = self.rpm * math.pi * self.tool.diameter / 60000
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

    def move(self, x=None, y=None, z=None, e=None, absolute=True, machine_coord=False, cut=False, comment=None):
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
            if e is not None:
                print(f" E{e:.4f}", end='')
            print(f" F{self.feed if cut else self.max_feed:.4f}", end='')
            print(f" ;{GREEN} {comment}{ENDC}" if comment else '')

    rapid = move

    def irapid(self, u=None, v=None, w=None, comment=None):
        self.move(u, v, w, absolute=False, cut=False, comment=comment)

    def cut(self, x=None, y=None, z=None, comment=None):
        self.move(x, y, z, absolute=True, cut=True, comment=comment)

    def icut(self, u=None, v=None, w=None, comment=None):
        self.move(u, v, w, absolute=False, cut=True, comment=comment)

    def retract(self, x=None, y=None, comment="Retract"):
        self.move(x, y, self.safe_z, comment=comment)

    def full_retract(self, comment="Full retract"):
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
        if diameter > 2 * self.tool.diameter:
            raise ValueError(f"{RED}Tool {self.tool.number} ({self.tool.diameter:.4f} mm) is less than half as wide as the hole ({diameter} mm).  Use a larger endmill or make a pocket instead of mill-drilling.")
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
        if diameter < self.tool.diameter:
            raise ValueError(f"{RED}Tool {self.tool.number} is too big ({self.tool.diameter:.4f} mm) to make this small ({diameter} mm) of a hole{ENDC}")
        if depth > self.tool.length:
            raise ValueError(f"{RED}Tool {self.tool.number} is shorter ({self.tool.length:.4f} mm) than the cut is deep ({depth} mm){ENDC}")
        if z_step > depth:
            raise ValueError(f"{RED}z_step cannot be greater than depth{ENDC}")
        if outside:
            diameter = -diameter
        self.absolute = True
        self.rapid(z=self.safe_z, comment="Rapid to Safe Z")
        self.rapid(c_x+diameter/2-self.tool.diameter/2, c_y, comment="Rapid to pocket offset")
        self.rapid(z=0.1, comment="Rapid to workpiece surface")
        print(f"G17;{GREEN} Helix in XY-plane{ENDC}")
        print(f"G2 Z{-depth} I{self.tool.diameter/2-diameter/2:.4f} J0 P{int(depth/z_step)} F{self.feed};{GREEN} Heli-drill{ENDC}")
        print(f"G2 I{self.tool.diameter/2-diameter/2:.4f} J0 P1 F{self.feed};{GREEN} Clean the bottom{ENDC}")
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
        if step is None: step = self.tool.diameter/10
        if diameter > 2 * self.tool.diameter:
            drill_diameter = 2*self.tool.diameter - 2*finish
        else:
            drill_diameter = diameter - 2*finish
        self.mill_drill(c_x, c_y, drill_diameter, depth, step, retract=False)
        center = self.tool.diameter/2-drill_diameter/2
        i = 0;
        for i in range(1, int((diameter/2-drill_diameter/2)/step)+1):
            if i%2:
                # Right to Left
                print(f"G2 I{center-i*step+step/2:.4f} X{c_x-drill_diameter/2+self.tool.diameter/2-i*step:.4f} F{self.feed}{'; '+GREEN+'Spiral out'+ENDC if i==1 else ''}")
            else:
                # Left to Right
                print(f"G2 I{i*step-step/2-center:.4f} X{c_x+drill_diameter/2-self.tool.diameter/2+i*step:.4f} F{self.feed}")
        if i%2:
            # Left to Right
            x2 = c_x+diameter/2-self.tool.diameter/2
            x1 = c_x+drill_diameter/2-self.tool.diameter/2+(i-1)*step
            print(f"G2 I{i*step-step/2-center+(x2-x1)/2:.4f} X{x2} F{self.feed}; {GREEN}Getting to final dimension{ENDC}")
            print(f"G2 I{self.tool.diameter/2-diameter/2} F{self.feed}; {GREEN}Final pass{ENDC}")
        else:
            # Right to Left
            x2 = c_x-diameter/2+self.tool.diameter/2
            x1 = c_x-drill_diameter/2+self.tool.diameter/2-(i-1)*step
            print(f"G2 I{center-i*step+step/2+(x2-x1)/2:.4f} X{x2} F{self.feed}; {GREEN}Getting to final dimension{ENDC}")
            print(f"G2 I{diameter/2-self.tool.diameter/2} F{self.feed}; {GREEN}Final pass{ENDC}")
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

    def frame(self, c_x, c_y, x, y, z_top=0, z_bottom=0, z_step=None, inside=False, retract=True, c='center', r=None, r_steps=10, feature=None):
        if feature: print(f";{ORANGE} {feature}{ENDC}")
        print(f";{CYAN} Rectangular Frame | [c_x,c_y]: {['{:.4f}'.format(c_x), '{:.4f}'.format(c_y)]}, x: {x:.4f}, y: {y:.4f}, z_top: {z_top}, z_bottom: {z_bottom}, z_step: {z_step}, inside: {inside}, c: {c}, r: {r}{ENDC}")

        if r is None:
            r = self.tool.radius if inside else 0
        if inside and r < self.tool.radius:
            raise ValueError(f"{RED}Tool radius ({self.tool.radius} mm) is larger than requested inside corner radius ({r} mm)")

        if not self.tool:
            raise ValueError(f"{RED}You can't cut a frame without selecting a tool first")

        depth = z_top - z_bottom
        if depth > self.tool.length:
            raise ValueError(f"{RED}Tool {self.tool.number} is shorter ({self.tool.length:.4f} mm) than frame is deep ({depth} mm){ENDC}")

        if not z_step:
            z_step = self.tool.diameter
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

        tool_d = -self.tool.diameter if inside else self.tool.diameter
        tool_r = tool_d/2

        turtle = self.turtle(verbose=True)
        turtle.penup()
        turtle.goto(flx+r, fly-tool_r, z_top, comment="Rapid to front-left corner:")
        turtle.pendown(z_top)
        for i in range(passes+1):
            if i == passes:
                z_step = 0
            turtle.forward(x-2*r, -z_step/4)
            turtle.circle(radius=r+tool_r, extent=90, steps=r_steps) # TODO: Implement smooth Turtle circles and drop the steps here
            turtle.forward(y-2*r, -z_step/4)
            turtle.circle(radius=r+tool_r, extent=90, steps=r_steps)
            turtle.forward(x-2*r, -z_step/4)
            turtle.circle(radius=r+tool_r, extent=90, steps=r_steps)
            turtle.forward(y-2*r, -z_step/4)
            turtle.circle(radius=r+tool_r, extent=90, steps=r_steps)

        self.retract()
        print(f";{CYAN} End Rectangular Frame{ENDC}")

    rectangle = frame

################################################################################
# Rectangular Pocket
################################################################################

    def rectangular_pocket(self, c_x, c_y, x, y, z_top=0, z_bottom=0, step=None, z_step=None, finish=0, undercut=False, retract=True, feature=None):
        if feature: print(f";{ORANGE} {feature}{ENDC}")
        print(f";{CYAN} Turtle Pocket | center: {['{:.4f}'.format(c_x), '{:.4f}'.format(c_y)]}, x: {x:.4f}, y: {y:.4f}, z_top: {z_top}, z_bottom: {z_bottom}, step: {step}, z_step: {z_step}, finish: {finish}, undercut: {undercut}, retract: {retract}{ENDC}")
        if not self.tool:
            raise ValueError(f"{RED}You can't cut a pocket without selecting a tool first")
        if self.tool.diameter > x or self.tool.diameter > y:
            raise ValueError(f"{RED}Tool {self.tool.number} is too big ({self.tool.diameter:.4f} mm) to make this small ({[x,y]} mm) of a pocket{ENDC}")
        depth = z_top - z_bottom
        if depth <= 0:
            raise ValueError(f"{RED}Pocket z_bottom must be lower than z_top")
        if depth > self.tool.max_depth:
            raise ValueError(f"{RED}Pocket is deeper ({depth} mm) than Tool {self.tool.number} can cut ({self.tool.length:.4f} mm){ENDC}")
        if depth > self.tool.flute_length:
            passes = math.ceil(depth/self.tool.flute_length)
            z_pass = depth/passes
            for i in range(passes):
                self.rectangular_pocket(c_x, c_y, x-2*finish, y-2*finish, z_top-i*z_pass, z_top-(i+1)*z_pass, step, z_step, None, undercut, retract if i==passes-1 else False)
            if finish:
                self.frame(c_x, c_y, x, y, z_top, z_bottom, step, inside=True, feature="Finishing pass inside depth")
                #TODO: Implement frame undercut
            return
        if finish:
            self.rectangular_pocket(c_x, c_y, x-2*finish, y-2*finish, z_top, z_bottom, step, z_step, None, undercut, retract=False)
            self.frame(c_x, c_y, x, y, z_top, z_bottom, step, inside=True, feature="Finishing pass inside finish")
        else:
            if z_step is None: z_step = self.tool.diameter
            z_passes = math.ceil(depth/z_step)
            z_step = depth/z_passes
            short = min(x,y)
            ramp_short = min(short-self.tool.diameter, 3/4*self.tool.diameter)
            long = max(x,y)
            ramp_long = ramp_short + long - short
            ramp_x = ramp_long if x > y else ramp_short
            ramp_y = ramp_long if y > x else ramp_short
            if step is None: step = self.tool.diameter/10
            passes = 2*math.ceil((x-ramp_x-self.tool.diameter)/step/2)
            if passes == 0:
                passes = 1
            step = (x-ramp_x-self.tool.diameter)/passes
            self.retract(comment="Retract")

            turtle = self.turtle()
            turtle._isdown = True
            turtle.goto(c_x-ramp_x/2, c_y+ramp_y/2, z_top)
            # Spiral Down
            for i in range(2*z_passes+2):
                turtle.forward(ramp_x, -z_step/4 if i < 2*z_passes else 0, comment=f"Ramp pass {i}")
                turtle.right(90)
                turtle.forward(ramp_y, -z_step/4 if i < 2*z_passes else 0, comment=f"Ramp pass {i}")
                turtle.right(90)
            # Spiral Out
            turtle.left(90)
            turtle.forward(step)
            turtle.right(90)
            for i in range(passes-2):
                turtle.forward(ramp_x+(i+1)*step)
                turtle.right(90)
                turtle.forward(ramp_y+(i+2)*step)
                turtle.right(90)

            # On final pass, ramp to final dimension (x,y,z) in one corner, then finish all four sides.
            # Add undercuts on each corner if needed
            d = self.tool.diameter
            h = d*math.sqrt(2)
            s = 1/2*(h-d)
            corner = math.sqrt((s**2)/2)

            turtle.forward(x-step-d)
            if undercut:
                turtle.left(45)
                turtle.forward(corner)
                turtle.back(corner)
                turtle.right(45)
            turtle.right(90)
            turtle.forward(y-d)
            if undercut:
                turtle.left(45)
                turtle.forward(corner)
                turtle.back(corner)
                turtle.right(45)
            turtle.right(90)
            turtle.forward(x-d)
            if undercut:
                turtle.left(45)
                turtle.forward(corner)
                turtle.back(corner)
                turtle.right(45)
            turtle.right(90)
            turtle.forward(y-d)
            if undercut:
                turtle.left(45)
                turtle.forward(corner)
                turtle.back(corner)
                turtle.right(45)
            turtle.right(90)
            turtle.forward(step)
            turtle.circle(-2*d, steps=10, extent=10)
        if retract:
            self.retract(c_x, c_y)

################################################################################
# Legacy Pocket
################################################################################

    def legacy_pocket(self, c_x, c_y, x, y, depth, step=None, finish=0.1, undercut=False, retract=True):
        print(f";{CYAN} Rectangular Pocket | center: {['{:.4f}'.format(c_x), '{:.4f}'.format(c_y)]}, x: {x:.4f}, y: {y:.4f}, depth: {depth}, step: {step}, finish: {finish}, undercut: {undercut}{ENDC}")
        if not self.tool:
            raise ValueError(f"{RED}You can't cut a pocket without selecting a tool first")
        if depth > self.tool.flute_length:
            raise ValueError(f"{RED}Tool {self.tool.number} flutes are shorter ({self.tool.flute_length:.4f} mm) than pocket is deep ({depth} mm){ENDC}")
        rough_depth = depth#-2*finish
        rough_x = x-2*finish
        rough_y = y-2*finish
        short = min(rough_x,rough_y)
        if short < self.tool.diameter:
            raise ValueError(f"{RED}Tool {self.tool.number} is too big ({self.tool.diameter:.4f} mm) to make this small ({short} mm) of a pocket{ENDC}")
        if step is None: step = self.tool.diameter/10

        # Ramp down to rough depth in the center, equidistant to each edge
        ramp_short = min(short-self.tool.diameter, 3/4*self.tool.diameter)
        long = max(rough_x,rough_y)
        ramp_long = ramp_short + long - short
        ramp_x = ramp_long if x > y else ramp_short
        ramp_y = ramp_long if y > x else ramp_short
        ramp_passes = 4*math.ceil(rough_depth/step/4)
        ramp_step = rough_depth / ramp_passes
        assert ramp_step <= step
        spiral_passes = 2*math.ceil((rough_x-ramp_x-self.tool.diameter)/step/2)
        if spiral_passes == 0:
            spiral_passes = 1
        spiral_step = (rough_x-ramp_x-self.tool.diameter)/spiral_passes
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
        d = self.tool.diameter
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
        return self.tool._description

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
            if self.tool:
                self.rapid(x=self._plotter['Slot Zero'][0], y=self._plotter['Slot Zero'][1], z=self._plotter['Z-Stage'], comment="Stage to retract current pen")
                self.rapid(z=self._plotter['Z-Click'], comment="Retract current pen")
                self.rapid(z=self._plotter['Z-Stage'], comment="Return to pen change stage")
            if value is None:
                self.x_offset = 0;
                self.y_offset = 0;
                rows = len(self._plotter['Magazine'])
                backset = self._plotter['Slot Zero'][1] + (rows+1)*self._plotter['Pen Spacing'];
                self.rapid(x=self._plotter['Slot Zero'][0], y=backset, comment="Rapid to homing-safe backset")
                return self.tool
            for row in self._plotter['Magazine']:
                if value in row:
                    i = row.index(value)
                    j = self._plotter['Magazine'].index(row)
                    self.x_offset = -i*self._plotter['Pen Spacing']
                    self.y_offset = j*self._plotter['Pen Spacing']
                    self.rapid(x=self._plotter['Slot Zero'][0], y=self._plotter['Slot Zero'][1], z=self._plotter['Z-Stage'], comment="Stage to activate new pen")
                    self.rapid(z=self._plotter['Z-Click'], comment="Activate new pen")
                    self.rapid(z=self._plotter['Z-Stage'], comment="Return to pen change stage")
                    self.tool = value
                    return self.tool
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
