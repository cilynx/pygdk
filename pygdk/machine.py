import json
import sys
import math

from .tool import Tool
from .turtle import Turtle
from .controller import Controller
from .accessories import Accessory

BLACK  = '\033[30m'
RED    = '\033[31m'
GREEN  = '\033[32m'
BROWN  = '\033[33m'
BLUE   = '\033[34m'
PURPLE = '\033[35m'
CYAN   = '\033[36m'
WHITE  = '\033[37m'
GREY   = '\033[90m'
ORANGE = '\033[91m'
LT_GREEN    = '\033[92m'
YELLOW      = '\033[93m'
LT_BLUE     = '\033[94m'
LT_PURPLE   = '\033[95m'
LT_CYAN     = '\033[96m'
LT_WHITE    = '\033[97m'
ENDC   = '\033[0m'

class Machine:

################################################################################
# Initializer -- Load details from JSON
################################################################################

    def __init__(self, json_file):
        if not json_file:
            raise ValueError(f"{RED}All machines must be initialized with a JSON config.  See https://github.com/cilynx/pygdk#quickstart for a quick introduction.")
        with open(f"machines/{json_file}") as f:
            self.dict = json.load(f)
            for req in ['Name', 'Max Feed Rate (mm/min)']:
                if not self.dict.get(req, None):
                    raise ValueError(f"{RED}All machines must have '{req}' defined in their JSON config.  See https://github.com/cilynx/pygdk/tree/main/machines for example configurations.")
            self.name = self.dict['Name']
            self.command_queue = [{'comment': f"Initializing Machine {self.name}", 'style': 'machine'}]
            self.controller = Controller(self.dict.get('Controller', None)) if self.dict.get('Controller', None) else None
            self.accessories = None
            if self.dict.get('Accessories', None):
                self.accessories = [Accessory(name, self.dict['Accessories'][name]) for name in self.dict['Accessories']]
            self.max_feed = self.dict['Max Feed Rate (mm/min)']
            self._x_offset = 0
            self._y_offset = 0
            self._z_offset = 0
            self._tool = None
            self._absolute = None
            self._feed = None
            self._css = 0
            self._turtle = None
            self._optimize = False
            self._x = None
            self._y = None
            self._z = None
            self._linear_moves = {None:[]}
            self._optimize_tool = None
            self._material = None
            self._x_clear = None
            self._y_clear = None
            self._z_clear = None
            self.gcode = None

################################################################################
# Command Queue
################################################################################

    def queue(self, **kwargs):
        self.command_queue.append(kwargs)

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
# Object representing the current Tool
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
        if 'Sharpie' not in self.tool._description:
            if previous_tool is None:
                self.queue(comment="Assuming first tool is already loaded", style='machine')
            else:
                self.queue(comment='Coming around for Tool Change', style='machine')
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
            self.queue(code=f"M6 T{tool}", comment=f"Select Tool {tool}", style='machine')
        else:
            self.queue(comment=f"Select Tool {tool}", style='machine')
        self.queue(comment=f"End Tool Change", style='machine')
        if self.material:
            self.update_fas()

################################################################################
# Tool Offsets
################################################################################

    @property
    def x_offset(self):
        return self._x_offset

    @x_offset.setter
    def x_offset (self, value):
        self.queue(comment=f"Setting x_offset: {value}", style='machine')
        self._x_offset = value

    @property
    def y_offset(self):
        return self._y_offset

    @y_offset.setter
    def y_offset (self, value):
        self.queue(comment=f"Setting y_offset: {value}", style='machine')
        self._y_offset = value

    @property
    def z_offset(self):
        return self._z_offset

    @z_offset.setter
    def z_offset (self, value):
        self.queue(comment=f"Setting z_offset: {value}", style='machine')
        self._z_offset = value

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
# Machine.max_rpm -- Used in speeds and feeds calculations.
################################################################################

    @property
    def max_rpm(self):
        return self._max_rpm

    @max_rpm.setter
    def max_rpm(self, value):
        self.queue(comment=f"Setting {self.name} max Spindle RPM: {value}", style='machine')
        self._max_rpm = value

################################################################################
# Machine.max_feed -- Used for rapids by default.
################################################################################

    @property
    def max_feed(self):
        return self._max_feed

    @max_feed.setter
    def max_feed(self, value):
        self.queue(comment=f"Setting {self.name} max Feed: {value} mm/min", style='machine')
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
    def feed(self, value):
        if value is None:
            raise ValueError(f"{RED}Machine.feed cannot be set to None")
        self._feed = value
        self.queue(comment=f"Using Feed: {self.feed:.4f} mm/min | {self.feed/25.4:.4f} in/min | {self.feed/25.4/12:.4f} ft/min", style='machine')

    @property
    def accel(self):
        if self._accel is not None:
            return self._accel
        else:
            raise ValueError(f"{RED}Machine.accel must be set prior to being queried")

    @accel.setter
    def accel(self, value):
        if value is None:
            raise ValueError(f"{RED}Machine.accel cannot be set to None")
        self._accel = value
        self.queue(code=f"M204 S{value}", comment="Set acceleration")

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
                self.queue(code='G90', comment='Absolute mode')
            else:
                self.queue(code='G91', comment='Incremental mode')

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
# Linear Moves -- Rapid, iRapid, LI, and iLI
################################################################################

    def move(self, x=None, y=None, z=None, e=None, absolute=True, machine_coord=False, li=False, comment=None):
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
            code = 'G53 G' if machine_coord else 'G'
            code += '1' if li else '0'
            if x is not None: self._x = x
            if y is not None: self._y = y
            if z is not None: self._z = z
            f = self.feed if li else self.max_feed
            self.queue(code=code, x=x, y=y, z=z, e=e, f=f, comment=comment)

    rapid = move

    def irapid(self, u=None, v=None, w=None, comment=None):
        self.move(u, v, w, absolute=False, li=False, comment=comment)

    def linear_interpolation(self, x=None, y=None, z=None, comment=None):
        self.move(x, y, z, absolute=True, li=True, comment=comment)

    def i_linear_interpolation(self, u=None, v=None, w=None, comment=None):
        self.move(u, v, w, absolute=False, li=True, comment=comment)

    def retract(self, x=None, y=None, comment="Retract"):
        self.move(x, y, self.safe_z, comment=comment)

    def full_retract(self, comment="Full retract"):
        self.move(z=0, machine_coord=True, comment=comment)

################################################################################
# Machine.bolt_circle() -- Make a Bolt Circle
################################################################################

    def bolt_circle(self, c_x, c_y, n, r, depth=0, theta=0):
        self.queue(comment=f"Bolt Circle | n:{n}, c:{[c_x,c_y]}, r:{r}, depth:{depth}", style='feature')
        self.rapid(z=10, comment="Rapid to Safe Z")
        theta = math.radians(theta)
        delta_theta = 2*math.pi/n
        for i in range(n):
            x = c_x + (r * math.cos(theta))
            y = c_y + (r * math.sin(theta))
            self.rapid(x, y, comment=f"Rapid to {i+1}")
            self.linear_interpolation(z=depth, comment=f"Drill {i+1}")
            self.rapid(z=10, comment="Retract")
            theta += delta_theta
        self.queue(comment='Bolt Circle | END', style='feature')

################################################################################
# Mill Drill - Helix-drill a hole up to 2x the diameter of the end mill used
################################################################################

    def mill_drill(self, c_x, c_y, diameter, depth, z_step=0.1, outside=False, retract=True):
        self.queue(comment=f"Mill Drill | center: {['{:.4f}'.format(c_x), '{:.4f}'.format(c_y)]}, diameter: {diameter:.4f}, depth: {depth}, z_step: {z_step:.4f}", style='feature')
        if diameter > 2 * self.tool.diameter:
            raise ValueError(f"{RED}Tool {self.tool.number} ({self.tool.diameter:.4f} mm) is less than half as wide as the hole ({diameter} mm).  Use a larger endmill or make a pocket instead of mill-drilling.")
        self.helix(c_x, c_y, diameter, depth, z_step, outside, retract)
        self.queue(comment='Mill Drill | END', style='feature')

################################################################################
# Helix - Helix-mill a circle with the cutter on either the inside (default)
#         or outside of the requested diameter
################################################################################

    def helix(self, c_x, c_y, diameter, depth, z_step=0.1, outside=False, retract=True):
        if self._optimize:
            raise ValueError(f"{RED}The _optimize option currently does not work with helix operations")
        self.queue(comment=f"Helix | center: {['{:.4f}'.format(c_x), '{:.4f}'.format(c_y)]}, diameter: {diameter:.4f}, depth: {depth}, z_step: {z_step:.4f}", style='feature')
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
        self.queue(code='G17', comment='Helix in XY-plane')
        self.queue(code='G2', z=-depth, i=self.tool.diameter/2-diameter/2, j=0, p=int(depth/z_step), f=self.feed, comment='Heli-drill')
        self.queue(code='G2', i=self.tool.diameter/2-diameter/2, j=0, p=1, f=self.feed, comment="Clean the bottom")
        if retract:
            self.rapid(z=self.safe_z, comment="Retract")
            self.rapid(c_x, c_y, comment="Re-Center")
        self.queue(comment='Helix | END', style='feature')

    circle = helix

################################################################################
# Circular Pocket
################################################################################

    def circular_pocket(self, c_x, c_y, diameter, depth, step=None, finish=0.1, retract=True):
        self.queue(comment=f"Circular Pocket | center: {['{:.4f}'.format(c_x), '{:.4f}'.format(c_y)]}, diameter: {diameter:.4f}, depth: {depth}, step: {step}, finish: {finish}", style='feature')
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
                self.queue(code='G2', i=center-i*step+step/2, x=c_x-drill_diameter/2+self.tool.diameter/2-i*step, f=self.feed, comment='Spiral out' if i==1 else '')
            else:
                # Left to Right
                self.queue(code='G2', i=i*step-step/2-center, x=c_x+drill_diameter/2-self.tool.diameter/2+i*step, f=self.feed)
        if i%2:
            # Left to Right
            x2 = c_x+diameter/2-self.tool.diameter/2
            x1 = c_x+drill_diameter/2-self.tool.diameter/2+(i-1)*step
            self.queue(code='G2', i=i*step-step/2-center+(x2-x1)/2, x=x2, f=self.feed, comment='Getting to final dimension')
            self.queue(code='G2', i=self.tool.diameter/2-diameter/2, f=self.feed, comment='Final pass')
        else:
            # Right to Left
            x2 = c_x-diameter/2+self.tool.diameter/2
            x1 = c_x-drill_diameter/2+self.tool.diameter/2-(i-1)*step
            self.queue(code='G2', i=center-i*step+step/2+(x2-x1)/2, x=x2, f=self.feed, comment='Getting to final dimension')
            self.queue(code='G2', i=diameter/2-self.tool.diameter/2, f=self.feed, comment='Final pass')
        if retract:
            self.rapid(c_x, c_y, self.safe_z, comment="Retract")
        self.queue(comment='Circular Pocket | END', style='feature')

################################################################################
# Machine.pocket_circle() -- Like a Bolt Circle, but with Circular Pockets
################################################################################

    def pocket_circle(self, c_x, c_y, n, r, depth, diameter, theta=0, step=None, finish=0.1):
        self.queue(comment=f"Pocket Circle | n:{n}, c:{[c_x,c_y]}, r:{r}, depth:{depth}, diameter:{diameter}, step:{step}, finish:{finish}", style='feature')
        self.rapid(z=10, comment="Rapid to Safe Z")
        theta = math.radians(theta)
        delta_theta = 2*math.pi/n
        for i in range(n):
            x = c_x + (r * math.cos(theta))
            y = c_y + (r * math.sin(theta))
            self.circular_pocket(x, y, diameter, depth, step, finish)
            theta += delta_theta
        self.queue(comment='Pocket Circle | END', style='feature')

################################################################################
# Rectangular Frame
################################################################################

    def frame(self, c_x, c_y, x, y, z_top=0, z_bottom=0, z_step=None, inside=False, retract=True, c='center', r=None, r_steps=10):
        self.queue(comment=f"Rectangular Frame | [c_x,c_y]: {['{:.4f}'.format(c_x), '{:.4f}'.format(c_y)]}, x: {x:.4f}, y: {y:.4f}, z_top: {z_top}, z_bottom: {z_bottom}, z_step: {z_step}, inside: {inside}, c: {c}, r: {r}", style='feature')

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
        self.queue(comment='Rectangular Frame | END', style='feature')

    rectangle = frame

################################################################################
# Rectangular Pocket
################################################################################

    def rectangular_pocket(self, c_x, c_y, x, y, z_top=0, z_bottom=0, step=None, z_step=None, finish=0, undercut=False, retract=True):
        self.queue(comment=f"Turtle Pocket | center: {['{:.4f}'.format(c_x), '{:.4f}'.format(c_y)]}, x: {x:.4f}, y: {y:.4f}, z_top: {z_top}, z_bottom: {z_bottom}, step: {step}, z_step: {z_step}, finish: {finish}, undercut: {undercut}, retract: {retract}", style='feature')
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

            turtle = self.turtle(verbose=True)
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
        self.queue(comment='Turtle Pocket | END', style='feature')


################################################################################
# Legacy Pocket
################################################################################

    def legacy_pocket(self, c_x, c_y, x, y, depth, step=None, finish=0.1, undercut=False, retract=True):
        self.queue(comment=f"Legacy Rectangular Pocket | center: {['{:.4f}'.format(c_x), '{:.4f}'.format(c_y)]}, x: {x:.4f}, y: {y:.4f}, depth: {depth}, step: {step}, finish: {finish}, undercut: {undercut}", style='feature')
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
            self.linear_interpolation(c_x-ramp_x/2, c_y+ramp_y/2, -(4*i+0)*ramp_step, comment = f"Ramp pass {i+1}")
            self.linear_interpolation(c_x+ramp_x/2, c_y+ramp_y/2, -(4*i+1)*ramp_step)
            self.linear_interpolation(c_x+ramp_x/2, c_y-ramp_y/2, -(4*i+2)*ramp_step)
            self.linear_interpolation(c_x-ramp_x/2, c_y-ramp_y/2, -(4*i+3)*ramp_step)
        self.linear_interpolation(c_x-ramp_x/2, c_y+ramp_y/2, -rough_depth, comment = f"Ramp pass {i+2}")
        self.linear_interpolation(c_x+ramp_x/2, c_y+ramp_y/2, -rough_depth)
        self.linear_interpolation(c_x+ramp_x/2, c_y-ramp_y/2, -rough_depth)
        self.linear_interpolation(c_x-ramp_x/2, c_y-ramp_y/2, -rough_depth)
        self.linear_interpolation(c_x-ramp_x/2, c_y+ramp_y/2, -rough_depth)
        # Spiral out to dimension-finish
        for i in range(0,int(spiral_passes/2)):
            self.linear_interpolation(c_x-ramp_x/2-i*spiral_step, c_y+ramp_y/2+i*spiral_step, comment=f"Spiral pass {i+1}")
            self.linear_interpolation(c_x+ramp_x/2+i*spiral_step, c_y+ramp_y/2+i*spiral_step)
            self.linear_interpolation(c_x+ramp_x/2+i*spiral_step, c_y-ramp_y/2-i*spiral_step)
            self.linear_interpolation(c_x-ramp_x/2-(i+1)*spiral_step, c_y-ramp_y/2-i*spiral_step)

        # On final pass, ramp to final dimension (x,y,z) in one corner, then finish all four sides.
        # Add undercuts on each corner if needed
        d = self.tool.diameter
        h = d*math.sqrt(2)
        s = 1/2*(h-d)
        corner = math.sqrt((s**2)/2)

        self.linear_interpolation(c_x-x/2+d/2, c_y+y/2-d/2, comment="Finishing pass")
        self.linear_interpolation(c_x+x/2-d/2, c_y+y/2-d/2)
        if undercut:
            self.linear_interpolation(c_x+x/2-d/2+corner, c_y+y/2-d/2+corner, comment="Top Left Undercut")
            self.linear_interpolation(c_x+x/2-d/2, c_y+y/2-d/2)
        self.linear_interpolation(c_x+x/2-d/2, c_y-y/2+d/2)
        if undercut:
            self.linear_interpolation(c_x+x/2-d/2+corner, c_y-y/2+d/2-corner, comment="Top Right Undercut")
            self.linear_interpolation(c_x+x/2-d/2, c_y-y/2+d/2)
        self.linear_interpolation(c_x-x/2+d/2, c_y-y/2+d/2)
        if undercut:
            self.linear_interpolation(c_x-x/2+d/2-corner, c_y-y/2+d/2-corner, comment="Bottom Right Undercut")
            self.linear_interpolation(c_x-x/2+d/2, c_y-y/2+d/2)
        self.linear_interpolation(c_x-x/2+d/2, c_y+y/2-d/2)
        if undercut:
            self.linear_interpolation(c_x-x/2+d/2-corner, c_y+y/2-d/2+corner, comment="Bottom Left Undercut")
            self.linear_interpolation(c_x-x/2+d/2, c_y+y/2-d/2)
        if retract:
            self.rapid(c_x, c_y, self.safe_z, comment="Retract")

        self.queue(comment='Legacy Rectangular Pocke | END', style='feature')

################################################################################
# Turtle Object Reference
################################################################################

    def turtle(self, x=0, y=0, z=0, z_draw=0, mode='standard', verbose=False):
        return Turtle(self, x, y, z, z_draw, mode, verbose)

################################################################################
# Modal State -- M70, M71, M72
################################################################################

    def save_modal_state(self):
        self.queue(code='M70', comment='Save Modal State')

    def invalidate_modal_state(self):
        self.queue(code='M71', comment='Invalidate Modal State')

    def restore_modal_state(self):
        self.queue(code='M72', comment='Restore Modal State')

################################################################################
# Modal State -- M70, M71, M72
################################################################################

    def pause(self, msg="Paused, Click Done to resume"):
        self.queue(code=f"M0 (MSG, {msg})")

################################################################################
# Generate G-code
################################################################################

    def generate_gcode(self):
        if self.dict.get('End G-Code',None):
            for line in self.dict.get('End G-Code'):
                self.command_queue.append({'code':line[0], 'comment':line[1]})
        self.gcode_array = []
        self.gcode = ''
        styles = {
            '': GREEN,
            'warning': RED,
            'machine': YELLOW,
            'feature': CYAN,
            'tool': BROWN,
            'turtle': PURPLE,
            'fdm_printer': ORANGE,
            'plotter': ORANGE,
            'lathe': ORANGE,
            'mill': ORANGE
        }
        for command in self.command_queue:
            line = ""
            if command.get('code',None) is not None:    # Code
                line += f"{command.get('code','')}"
            if command.get('x',None) is not None:       # X-coordinate
                line += f" X{command['x']:.4f}"
            if command.get('y',None) is not None:       # Y-coordinate
                line += f" Y{command['y']:.4f}"
            if command.get('z',None) is not None:       # Z-coordinate
                line += f" Z{command['z']:.4f}"
            if command.get('e',None) is not None:       # Extruder Position
                line += f" E{command['e']:.4f}"
            if command.get('i',None) is not None:       # Arc Center X-offset
                line += f" I{command['i']:.4f}"
            if command.get('j',None) is not None:       # Arc Center Y-offset
                line += f" J{command['j']:.4f}"
            if command.get('p',None) is not None:       # Number of helix turns
                line += f" P{command['p']}"
            if command.get('f',None) is not None:       # Feed Rate
                line += f" F{command['f']:.4f}"
            if command.get('s',None) is not None:       # Spindle RPM, Bed/Hotend Temperature
                line += f" S{command['s']:.4f}"
            if command.get('comment',None) is not None: # Human-readable comments
                line += f"; {styles[command.get('style', '')]}{command.get('comment', '')}{ENDC}"
            self.gcode_array.append(line)
        self.gcode = "\n".join(self.gcode_array)

################################################################################
# Print G-code to stdout
################################################################################

    def print_gcode(self):
        if not self.gcode:
            self.generate_gcode()
        print(self.gcode)

################################################################################
# Save G-code to File
################################################################################

    def save_gcode(self, filename=sys.argv[0]+'.nc'):
        if not self.gcode:
            self.generate_gcode()
        with open(filename, 'w') as file:
            file.write(self.gcode)

################################################################################
# OctoPrint Helper
################################################################################

    def octoprint(self, start=False, select=True):
        print(f"{GREEN}Sending to OctoPrint{' and starting print' if start else ''}{ENDC}")
        host = self.controller.get("Hostname / IP", None)
        api_key = self.controller.get("API Key", None)
        if not host or not api_key:
            raise ValueError("You must configure `Hostname / IP` and `API Key` in the `Controller` section of your machine JSON before you can send to OctoPrint.  See https://github.com/cilynx/pygdk/tree/main/machines for configuration examples.")
        if not self.gcode:
            self.generate_gcode()
        import os, requests
        filename = os.path.basename(sys.argv[0])+'.g'
        fle={'file': (filename, self.gcode)}
        url=f"http://{host}/api/files/local"
        payload={'select': select, 'print': start }
        header={'X-Api-Key': api_key }
        response = requests.post(url, files=fle,data=payload,headers=header)
        print(response.__dict__)

    OctoPrint = octoprint

################################################################################
# Buildbotics / Onefinity Helper
################################################################################

    def buildbotics(self, start=False):
        print(f"{GREEN}Sending to Buildbotics Controller{' and starting job' if start else ''}{ENDC}")
        host = self.controller.get("Hostname / IP", None)
        if not host:
            raise ValueError("You must configure `Hostname / IP` in the `Controller` section of your machine JSON before you can send to your Buildbotics Controller.  See https://github.com/cilynx/pygdk/tree/main/machines for configuration examples.")
        if not self.gcode:
            self.generate_gcode()
        import os, requests
        filename = os.path.basename(sys.argv[0])+'.nc'
        gcode={'gcode': (filename, self.gcode)}
        response = requests.put(f"http://{host}/api/file", files=gcode)
        print(response.__dict__)
        if start:
            response = requests.put(f"http://{host}/api/start")
            print(response.__dict__)

    Buildbotics = buildbotics
    onefinity = buildbotics
    Onefinity = buildbotics

################################################################################
# Power On/Off
################################################################################

    def power_on(self):
        print("Machine.power_on()")
        for accessory in self.accessories:
            if accessory.before:
                print(f"Powering on {accessory.name}")
                accessory.power_on()

        print("Powering on Controller")
        self.controller.power_on()

        for accessory in self.accessories:
            if accessory.after:
                print(f"Powering on {accessory.name}")
                accessory.power_on()

    def power_off(self):
        print("Machine.power_off()")
        for accessory in self.accessories:
            if accessory.before:
                print(f"Powering off {accessory.name}")
                accessory.power_off()

        self.controller.power_off()

        for accessory in self.accessories:
            if accessory.after:
                print(f"Powering off {accessory.name}")
                accessory.power_off()

################################################################################
# Gcode Upload Dispatcher
################################################################################

    def send_gcode(self, start=False):
        self.power_on()
        if self.controller.get('Flavor', None).lower() == 'octoprint':
            self.octoprint(start)
        elif self.controller.get('Flavor', None).lower() == 'buildbotics':
            self.buildbotics(start)
        else:
            raise ValueError(f"{RED}You must configure `Controller` ('OctoPrint' or 'Buildbotics') in your machine JSON to use dispatched upload.")

    upload_gcode = send_gcode

################################################################################
# Camotics Helper
################################################################################

    def camotics(self, filename=sys.argv[0]+'.nc'):
        import os
        self.save_gcode(filename)
        os.system(f"camotics {filename}")

    CAMotics = camotics
