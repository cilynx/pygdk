import math
import random
import copy

RED  = '\033[31m' # Red
CYAN   = '\033[36m'
YELLOW = '\033[93m' # Yellow
ENDC  = '\033[0m'  # End Color

class Turtle:

################################################################################
# Turtle.__init__() -- Initializer
################################################################################

    def __init__(self, machine, x=0, y=0, z=0, z_draw=0, mode='standard', verbose=False):
        self._pencolor = None
        self._verbose = verbose
        self._machine = machine
        self._isdown = False
        self._mode = mode
        self.heading = [1,0,0]
        self.normal = [0,0,1]
        self.right_v = [0,-1,0]
        self._x = x
        self._y = y
        self._z = z
        self._z_draw = z_draw
        if verbose: machine.queue(comment=f"Turtle | [x,y,z]: {[x,y,z]}", style='turtle')
#        machine.retract()

    def __del__(self):
        self._machine.queue(comment='Turtle | END', style='turtle')

################################################################################
# Turtle.forward(distance)
# Turtle.fd(distance)
#
# Move the turtle forward by the specified distance, in the direction the turtle
# is headed.
################################################################################

    def forward(self, distance, dz=0, e=None, comment=None):
        x = self._x + distance * self.heading[0]
        y = self._y + distance * self.heading[1]
        if dz: # 2.5D motion
            if self.heading[2] == 0:
                z = self._z + dz
            else:
                raise ValueError(f"{RED}You can only use 2.5D motion in the XY-plane")
        else: # 3D motion
            z = self._z + distance * self.heading[2]
        if self._verbose and comment is None:
            comment = f"Moving at {[round(i,4) for i in self.heading]} from ({self._x:.4f}, {self._y:.4f}, {self._z:.4f}) to ({x:.4f}, {y:.4f}, {z:.4f})"
        self.goto(x, y, z, e, comment=comment)

    fd = forward

################################################################################
# Turtle.back(distance)
# Turtle.bk(distance)
# Turtle.backward(distance)
#
# Move the turtle backward by distance, opposite to the direction the turtle is
# headed. Do not change the turtle’s heading.
################################################################################

    def back(self, distance, dz=0):
        self.forward(-distance, dz)

    backward = back
    bk = back

################################################################################
# Rotation Matrix -- Heavy Math Helpers for Roll, Pitch, and Yaw
################################################################################

    def rot(self, n, angle):
        cos = math.cos(angle)
        sin = math.sin(angle)
        return [ [cos+(n[0]**2)*(1-cos),         n[0]*n[1]*(1-cos)-n[2]*sin,     n[0]*n[2]*(1-cos)+n[1]*sin],
                 [n[0]*n[1]*(1-cos)+n[2]*sin,    cos+(n[1]**2)*(1-cos),          n[1]*n[2]*(1-cos)-n[0]*sin],
                 [n[0]*n[2]*(1-cos)-n[1]*sin,    n[1]*n[2]*(1-cos)+n[0]*sin,     cos+(n[2]**2)*(1- cos)] ]
        # http://scipp.ucsc.edu/~haber/ph216/rotation_12.pdf

    def dot(self, m1, m2):
        # https://stackoverflow.com/questions/10508021/matrix-multiplication-in-pure-python
        dp = [[sum(x*y for x,y in zip(m1_r, m2_c)) for m2_c in zip(*m2)] for m1_r in m1]

        # I hate this, but w/o it, cumulative error gets crazy after a few hundred rotations
        # It basically "snaps" to an axis if you're within 0.000000000001 of it
        if round(dp[0][0],12) == 0: dp[0][0] = 0
        if round(dp[0][0],12) == 1: dp[0][0] = 1
        if round(dp[0][1],12) == 0: dp[0][1] = 0
        if round(dp[0][1],12) == 1: dp[0][1] = 1
        if round(dp[0][2],12) == 0: dp[0][2] = 0
        if round(dp[0][2],12) == 1: dp[0][2] = 1

        return dp

    def mag(self, vector):
        return sum(i*i for i in vector)

################################################################################
# Turtle.roll - Roll side to side without changing the heading vector
################################################################################

    def roll(self, angle):
        angle = math.radians(angle)
        self.right_v = self.dot([self.right_v], self.rot(self.heading, angle))[0]
        self.normal = self.dot([self.normal], self.rot(self.heading, angle))[0]

################################################################################
# Turtle.pitch - Tilt up or down without changing the side vector
################################################################################

    def pitch(self, angle):
        angle = -math.radians(angle)
        self.heading = self.dot([self.heading], self.rot(self.right_v, angle))[0]
        self.normal = self.dot([self.normal], self.rot(self.right_v, angle))[0]

    def pitchrr(self, rise, run):
        angle = -math.atan2(rise, run)
        self.heading = self.dot([self.heading], self.rot(self.right_v, angle))[0]
        self.normal = self.dot([self.normal], self.rot(self.right_v, angle))[0]

################################################################################
# Turtle.yaw - Rotate right or left as viewed from above without changing the
# normal vector
################################################################################

    def yaw(self, angle):
        angle = math.radians(angle)
        self.heading = self.dot([self.heading], self.rot(self.normal, angle))[0]
        self.right_v = self.dot([self.right_v], self.rot(self.normal, angle))[0]

    right = yaw
    rt = yaw

    def left(self, angle):
        self.yaw(-angle)

    lt = left

################################################################################
# Turtle.goto(x, y=None)
# Turtle.setpos(x, y=None)
# Turtle.setposition(x, y=None)
#
# If y is None, x must be a pair of coordinates or a Vec2D (e.g. as returned by
# pos()).
#
# Move turtle to an absolute position. If the pen is down, draw line. Do not
# change the turtle’s orientation.
################################################################################

    def goto(self, x=None, y=None, z=None, e=None, comment=None):
        if x is not None:
            self._x = x
        if y is not None:
            self._y = y
        if z is not None:
            self._z = z
        self._machine.move(self._x, self._y, self._z, e, li=self._isdown, comment=comment)

    setpos = goto
    setposition = goto

################################################################################
# Turtle.delta(x, y, z, e)
#
# Move by the requested parameter in each axis, regardless of heading
################################################################################

    def delta(self, x=None, y=None, z=None, e=None, comment=None):
        if x is not None:
            self._x = self._x + x
        if y is not None:
            self._y = self._y + y
        if z is not None:
            self._z = self._z + z
        self._machine.move(self._x, self._y, self._z, e, li=self._isdown, comment=comment)


################################################################################
# Turtle.setx(x)
#
# Set the turtle’s first coordinate to x, leave second coordinate unchanged.
# If the pen is down, draw line.
################################################################################

    def setx(self, x):
        self.goto(x, self._y)

################################################################################
# Turtle.sety(y) -- Teleport the Turtle to a new Y-position
#
# Set the turtle’s second coordinate to y, leave first coordinate unchanged.
# If the pen is down, draw line.
################################################################################

    def sety(self, y):
        self.goto(self._x, y)

################################################################################
# Turtle.home()
#
# Move turtle to the origin – coordinates (0,0) – and set its heading to its
# start-orientation (which depends on the mode, see mode()). Do not draw a line.
################################################################################

    def home(self):
        wasdown = self._isdown
        self.penup()
        self.goto(0,0)
        if wasdown:
            self.pendown()
        self.heading = [1,0,0]
#        self.yaw = 0 if self._mode == "logo" else -90

    reset = home

################################################################################
# Turtle.circle(radius, extent=None, steps=None)
#
# Draw a circle with given radius. The center is radius units left of the
# turtle; extent – an angle – determines which part of the circle is drawn. If
# extent is not given, draw the entire circle. If extent is not a full circle,
# one endpoint of the arc is the current pen position. Draw the arc in
# counterclockwise direction if radius is positive, otherwise in clockwise
# direction. Finally the direction of the turtle is changed by the amount of
# extent.
#
# As the circle is approximated by an inscribed regular polygon, steps
# determines the number of steps to use. If not given, it will be calculated
# automatically. May be used to draw regular polygons.
################################################################################

    def circle(self, radius, extent=360, steps=10, comment=None):
        side = abs(2*radius*math.sin(math.pi*extent/360/steps))
        angle = extent/steps if radius > 0 else -extent/steps
        self.left(angle/2)
        self.forward(side, comment=comment)
        for i in range(steps-1):
            self.left(angle)
            self.forward(side, comment=comment)
        self.left(angle/2)

################################################################################
# Turtle.speed(speed=None)
#
# Deliberately not implemented.  You want to set your feeds and speeds outside
# of the Turtle framework.  Turtle shouldn't care what you're cutting or drawing
# on or with.
################################################################################

    def speed(self, speed=None):
        self.queue(comment="Turtle.speed() is deliberately not implemented.", style='warning')
        self.queue(comment="You want to set your feeds and speeds outside of the Turtle framework.", style='warning')
        self.queue(comment="Turtle shouldn't care what you're cutting or drawing on or with.", style='warning')

################################################################################
# Turtle.position()
# Turtle.pos()
#
# Return the turtle’s current location (x,y) (as a Vec2D vector).
################################################################################

    def position(self):
        return [self._x, self._y, self._z]

    pos = position

################################################################################
# Turtle.towards(x, y=None)
#
# Returns the angle between the line from turtle position to position specified
# by (x,y), the vector.  This depends on the turtle's start orientation which
# depends on the mode - "standard" or "logo".
################################################################################

    def towards(self, x, y=None):
        raise NotImplementedError

################################################################################
# Turtle.xcor()
#
# Returns the turtle's x coordinate
################################################################################

    def xcor(self):
        return self._x

################################################################################
# Turtle.ycor()
#
# Returns the turtle's y coordinate
################################################################################

    def ycor(self):
        return self._y

################################################################################
# Turtle.distance(x, y=None)
#
# Return the distance from the turtle to (x,y) or the given vector.
################################################################################

    def distance(self, x, y=None):
        if y is None:
            y = x[1]
            x = x[0]
        return ((x-self._x)**2+(y-self._y)**2)**0.5

################################################################################
# Turtle.pendown()
# Turtle.pd()
# Turtle.down()
#
# Pull the pen down -- drawing / cutting when moving
################################################################################

    def pendown(self, z=None):
        self._isdown = True
        if z is not None:
            self._z_draw = z
        self._z = self._z_draw
        self._machine.linear_interpolation(z=self._z, comment="Pendown" if self._verbose else None)

    pd = pendown
    down = pendown

################################################################################
# Turtle.penup()
# Turtle.pu()
# Turtle.up()
#
# Pull the pen up -- no drawing / cutting when moving
################################################################################

    def penup(self):
        self._isdown = False
        self._machine.retract(comment="Penup" if self._verbose else None)
        self._z = self._machine.safe_z

    pu = penup
    up = penup


################################################################################
# Turtle.pencolor(color=None)
#
# Return or set the pencolor.
#
# pencolor()
#
# Return the current pencolor as color specification string or as a tuple (see
# example). May be used as input to another color/pencolor/fillcolor call.
#
# pencolor(colorstring)
#
# Set pencolor to colorstring, which is a color specification string, such as
# "Red".  Colors must be defined in your plotter magazine in your machine JSON.
#
# TODO: Nearest color matching to enable the other standard modes.
################################################################################

    def pencolor(self, color=None, next=None):
        if color is not None:
            self._machine.pen_color = color
            self._pencolor = color
        if next is not None:
            self.goto(next[0], next[1], comment="Going to requested next position after color change")
        else:
            self.goto(self._x, self._y, comment="Going back to Turtle's (x,y) after color change")
        if self._isdown:
            self.pendown()
        return self._pencolor

################################################################################
# Turtle.mode(mode=None)
#
# Set turtle mode (“standard”, “logo” or “world”) and perform reset. If mode is
# not given, current mode is returned.
#
# Mode “standard” is compatible with old turtle. Mode “logo” is compatible with
# most Logo turtle graphics. Mode “world” uses user-defined “world coordinates”.
# Attention: in this mode angles appear distorted if x/y unit-ratio doesn’t
# equal 1.
#
# Mode          Initial Turtle Heading      Positive Angles
# “standard”    to the right (east)         counterclockwise
# “logo”        upward (north)              clockwise
################################################################################

    def mode(self, mode=None):
        if mode is None:
            return self._mode
        elif mode == "logo" or mode == "standard":
            self._mode = mode
            self.reset()
        else:
            raise ValueError(f"{RED}Turtle.mode can only be set to \"logo\" or \"standard\"")

################################################################################
# L-system
################################################################################

    @property
    def orientation(self):
        return self.heading, self.normal

    @orientation.setter
    def orientation(self, value):
        self.heading, self.normal = value

    def lsystem(self, name=None, axiom=None, rules=None, n=None, seg=10, angle=None, arms=None, lift=True):
        import json
        if name is not None:
            self._machine.queue(comment='Loading L-system from JSON', style='turtle')
            with open(f"tables/l-systems.json") as f:
                systems = json.load(f)
                system = systems.get(name,None)
                if system is None:
                    raise ValueError(f"{RED}{name} doesn't appear to be defined.  See `tables/l-systems.json` for all known systems{ENDC}")
                if axiom is None: axiom = system['axiom']
                if rules is None: rules = system['rules']
                if angle is None: angle = system['angle']
                if n is None: n = system['n']
                lift = system.get('lift',lift)

        safe_z = self._machine.safe_z
        if lift is False:
            self._machine.safe_z = self._z_draw

        if arms is not None:
            angle = 360/arms
            axiom = '--'.join(['F' for F in range(arms)])

        if None in [axiom, rules, angle, n]:
            raise ValueError(f"{RED}L-systems must have axiom, rules, angle, and n defined.{ENDC}")

        seq = axiom
        for _ in range(n):
            _rules = copy.deepcopy(rules)
            for rule in _rules:
                if isinstance(_rules[rule], list):
                    _rules[rule] = random.choice(_rules[rule])
                elif isinstance(_rules[rule], dict):
                    options = []
                    weights = []
                    for option in _rules[rule]:
                        options.append(option)
                        weights.append(_rules[rule][option])
                    _rules[rule] = random.choices(options, weights, k=1)[0]
            seq = ''.join([_rules.get(c,c) for c in seq])

#        print(seq)
        stack = []
        for command in seq:
            if command in ['F','G']:
                if not self._isdown:
                    self.pendown()
                self.forward(seg)
            elif command == 'f':
                if self._isdown and lift:
                    self.penup()
                self.forward(seg)
            elif command == '@':
                seg = seg*1/(2**0.5)
            elif command == '+':
                self.right(angle)
            elif command == '-':
                self.left(angle)
            elif command == '[':
                stack.append((self.position(), self.orientation, seg))
            elif command == ']':
                position, orientation, seg = stack.pop()
                if position != self.position():
                    if self._isdown and lift:
                        self.penup()
                    self.goto(position[0], position[1])
                self.orientation = orientation
        self._machine.safe_z = safe_z

################################################################################
# Bethlehem Star
#
# r1 is the radius of circle of the inside vertices
# r2 is the four smallest points
# r3 is the three medium points on top
# r4 is the long point on the bottom
################################################################################

    def bethlehem_star(self, r1, r2, r3, r4):
        angle = math.radians(-90)
        self.right(90)
        self.forward(r4) # Start at the bottom
        self.pendown()
        for i in range(3):
            angle += math.radians(22.5) # Inside vertex
            self.goto(r1*math.cos(angle), r1*math.sin(angle))
            angle += math.radians(22.5) # Small point
            self.goto(r2*math.cos(angle), r2*math.sin(angle))
            angle += math.radians(22.5) # Inside vertex
            self.goto(r1*math.cos(angle), r1*math.sin(angle))
            angle += math.radians(22.5) # Medium Point
            self.goto(r3*math.cos(angle), r3*math.sin(angle))
        angle += math.radians(22.5) # Inside vertex
        self.goto(r1*math.cos(angle), r1*math.sin(angle))
        angle += math.radians(22.5) # Small point
        self.goto(r2*math.cos(angle), r2*math.sin(angle))
        angle += math.radians(22.5) # Inside vertex
        self.goto(r1*math.cos(angle), r1*math.sin(angle))
        angle += math.radians(22.5) # Long Point
        self.goto(r4*math.cos(angle), r4*math.sin(angle))
        self.penup()

################################################################################
# Heightmaps
################################################################################

    def heightmap(self, filename, z_bottom=-10, x=None, y=None, invert=False, res=1):
        from PIL import Image, ImageOps
        im = Image.open(filename).convert("L")
        width, height = im.size
        if x is not None:
            im = im.resize((res*int(x), res*int(x*height/width)))
            width, height = im.size
        if invert:
            im = ImageOps.invert(im)
        pixels = im.load()
        self.pendown()
        odd = False
        first = True
        for y in range(height):
            odd = not odd
            for x in range(width):
                _x = x if odd else width-x-1
                _z = pixels[_x,height-y-1]/255*z_bottom
                if _z != 0:
                    if first:
                        self.goto(_x/res,y/res)
                        first = False
                    self.goto(_x/res,y/res,_z)
        self.penup()

################################################################################
# Geometric Primitives
################################################################################

    def rectangle(self, start=[0,0], width=10, height=10, tool_d=1, stepover=False):
        self.penup()
        self.goto(start[0], start[1])
        self.heading = [0,1,0]
        if stepover:
            self.pendown()
            self.forward(height-tool_d)
            cut = tool_d
            while height-cut > 0:
                self.right(90)
                self.forward(height-cut)
                self.right(90)
                self.forward(height-cut)
                cut += stepover
            self.penup()

################################################################################
# Stick Lettering
################################################################################

    def draw_m(self, start=[0,0], height=10):
        scale = height/10
        self._machine.x_offset += start[0]
        self._machine.y_offset += start[1]
        self.penup()
        self.goto(0,5*scale)            # start at the top of the 1st vertical line
        self.pendown()
        self.goto(0,0)            # draw the vertical bar
        self.goto(0,3*scale)            # go to the start of the 1st hump
        self.heading = [0,1,0]
        self.circle(-2*scale, 180)      # draw the first hump
        self.goto(4*scale,1*scale)            # drap the middle vertical line
        self.goto(4*scale,3*scale)            # go to the start of the 2nd hump
        self.heading = [0,1,0]
        self.circle(-2*scale, 180)      # draw the second hump
        self.goto(8*scale,0)            # drap the third vertical line
        self.penup()
        self._machine.x_offset -= start[0]
        self._machine.y_offset -= start[1]
        return(8*scale)

    def draw_1(self, start=[0,0], height=10):
        scale = height/10
        self._machine.x_offset += start[0]
        self._machine.y_offset += start[1]
        self.penup()
        self.goto(0, 10*scale)
        self.pendown()
        self.goto(0, 0)
        self.penup()
        self._machine.x_offset -= start[0]
        self._machine.y_offset -= start[1]
        return(1*scale)

    def draw_2(self, start=[0,0], height=10):
        scale = height/10
        self._machine.x_offset += start[0]
        self._machine.y_offset += start[1]
        self.penup()
        self.goto(0, 10*scale)
        self.heading = [1,0,0]
        self.pendown()
        self.forward(5*scale)
        self.right(90)
        self.forward(5*scale)
        self.right(90)
        self.forward(5*scale)
        self.left(90)
        self.forward(5*scale)
        self.left(90)
        self.forward(5*scale)
        self.penup()
        self._machine.x_offset -= start[0]
        self._machine.y_offset -= start[1]
        return(5*scale)

    def draw_3(self, start=[0,0], height=10):
        scale = height/10
        self._machine.x_offset += start[0]
        self._machine.y_offset += start[1]
        self.penup()
        self.goto(0, 10*scale)
        self.heading = [1,0,0]
        self.pendown()
        self.forward(5*scale)
        self.right(90)
        self.forward(10*scale)
        self.right(90)
        self.forward(5*scale)
        self.penup()
        self.right(90)
        self.forward(5*scale)
        self.right(90)
        self.forward(2.5*scale)
        self.pendown()
        self.forward(2.5*scale)
        self.penup()
        self._machine.x_offset -= start[0]
        self._machine.y_offset -= start[1]
        return(5*scale)

    def draw_4(self, start=[0,0], height=10):
        scale = height/10
        self._machine.x_offset += start[0]
        self._machine.y_offset += start[1]
        self.penup()
        self.goto(0, 10*scale)
        self.heading = [0,-1,0]
        self.pendown()
        self.forward(5*scale)
        self.left(90)
        self.forward(5*scale)
        self.penup()
        self.right(90)
        self.backward(5*scale)
        self.pendown()
        self.forward(10*scale)
        self.penup()
        self._machine.x_offset -= start[0]
        self._machine.y_offset -= start[1]
        return(5*scale)

    def draw_5(self, start=[0,0], height=10):
        scale = height/10
        self._machine.x_offset += start[0]
        self._machine.y_offset += start[1]
        self.penup()
        self.goto(5*scale, 10*scale)
        self.heading = [-1,0,0]
        self.pendown()
        self.forward(5*scale)
        self.left(90)
        self.forward(5*scale)
        self.left(90)
        self.forward(5*scale)
        self.right(90)
        self.forward(5*scale)
        self.right(90)
        self.forward(5*scale)
        self.penup()
        self._machine.x_offset -= start[0]
        self._machine.y_offset -= start[1]
        return(5*scale)

    def draw_6(self, start=[0,0], height=10):
        scale = height/10
        self._machine.x_offset += start[0]
        self._machine.y_offset += start[1]
        self.penup()
        self.goto(5*scale, 10*scale)
        self.heading = [-1,0,0]
        self.pendown()
        self.forward(5*scale)
        self.left(90)
        self.forward(10*scale)
        self.left(90)
        self.forward(5*scale)
        self.left(90)
        self.forward(5*scale)
        self.left(90)
        self.forward(5*scale)
        self.penup()
        self._machine.x_offset -= start[0]
        self._machine.y_offset -= start[1]
        return(5*scale)

    def draw_7(self, start=[0,0], height=10):
        scale = height/10
        self._machine.x_offset += start[0]
        self._machine.y_offset += start[1]
        self.penup()
        self.goto(0, 7.5*scale)
        self.heading = [0,1,0]
        self.pendown()
        self.forward(2.5*scale)
        self.right(90)
        self.forward(5*scale)
        self.right(90)
        self.forward(10*scale)
        self.penup()
        self._machine.x_offset -= start[0]
        self._machine.y_offset -= start[1]
        return(5*scale)

    def draw_8(self, start=[0,0], height=10):
        scale = height/10
        self._machine.x_offset += start[0]
        self._machine.y_offset += start[1]
        self.penup()
        self.goto(5*scale, 5*scale)
        self.heading = [0,1,0]
        self.pendown()
        self.forward(5*scale)
        self.left(90)
        self.forward(5*scale)
        self.left(90)
        self.forward(10*scale)
        self.left(90)
        self.forward(5*scale)
        self.left(90)
        self.forward(5*scale)
        self.left(90)
        self.forward(5*scale)
        self.penup()
        self._machine.x_offset -= start[0]
        self._machine.y_offset -= start[1]
        return(5*scale)

    def draw_9(self, start=[0,0], height=10):
        scale = height/10
        self._machine.x_offset += start[0]
        self._machine.y_offset += start[1]
        self.penup()
        self.goto(5*scale, 5*scale)
        self.heading = [-1,0,0]
        self.pendown()
        self.forward(5*scale)
        self.right(90)
        self.forward(5*scale)
        self.right(90)
        self.forward(5*scale)
        self.right(90)
        self.forward(10*scale)
        self.penup()
        self._machine.x_offset -= start[0]
        self._machine.y_offset -= start[1]
        return(5*scale)

    def draw_0(self, start=[0,0], height=10):
        scale = height/10
        self._machine.x_offset += start[0]
        self._machine.y_offset += start[1]
        self.penup()
        self.goto(0, 0)
        self.heading = [1,0,0]
        self.pendown()
        self.forward(5*scale)
        self.left(90)
        self.forward(10*scale)
        self.left(90)
        self.forward(5*scale)
        self.left(90)
        self.forward(10*scale)
        self.penup()
        self._machine.x_offset -= start[0]
        self._machine.y_offset -= start[1]
        return(5*scale)

    def draw_dot(self, start=[0,0], height=10):
        scale = height/10
        self._machine.x_offset += start[0]
        self._machine.y_offset += start[1]
        self.penup()
        self.goto(0, 0)
        self.pendown()
        self.goto(0, 1*scale)
        self.penup()
        self._machine.x_offset -= start[0]
        self._machine.y_offset -= start[1]
        return(1*scale)

    def write(self, text=None, start=[0,0], height=10):
        scale = height/10
        dispatcher = {
            'm': self.draw_m,
            '1': self.draw_1,
            '2': self.draw_2,
            '3': self.draw_3,
            '4': self.draw_4,
            '5': self.draw_5,
            '6': self.draw_6,
            '7': self.draw_7,
            '8': self.draw_8,
            '9': self.draw_9,
            '0': self.draw_0,
            '.': self.draw_dot,
        }
        for char in str(text):
            draw_char = dispatcher.get(char)
            start[0] += draw_char(start, height) + scale

################################################################################
# Squirtle -- A turtle that extrudes filament
################################################################################

class Squirtle(Turtle):
    def __init__(self, printer, verbose=False):
        super().__init__(printer, verbose)
        self.printer = printer
        self.extrusion_multiplier = 1
        self.extrude = False
        self.e = 0

    # def __del__(self):
    #     self.penup()
    #     super().__del__()

    def penup(self):
        self.e -= self.printer.retract_f
        self.goto(e=self.e, comment="Retract filament")
        self.extrude = False
        self._isdown = False

    def pendown(self, prime=True):
        if prime:
            self.e += self.printer.retract_f + self.printer.extra_push
            self.goto(e=self.e, comment="Prime filament")
        self.extrude = True
        self._isdown = True

    def pencolor(self):
        self.queue(comment="Pen colors are disabled for Squirtle.  Maybe someday I'll play with multiple extruders.", style='warning')

    def forward(self, distance, dz=0, comment=None):
        if self.extrude:
            #TODO: Filament object
            self.e = self.e + self.extrusion_multiplier*(self._machine.nozzle_d*distance*0.2)/(math.pi*(1.75/2)**2)
            comment = f"Push {self.extrusion_multiplier*(self._machine.nozzle_d*distance*0.2)/(math.pi*(1.75/2)**2):.4f}mm of filament"
        super().forward(distance, dz, self.e, comment)

    def goto(self, x=None, y=None, z=None, e=None, comment=None):
        if x is None: x = self._x
        if y is None: y = self._y
        if z is None: z = self._z
        if self.extrude:
            distance = ( (x-self._x)**2 + (y-self._y)**2 + (z-self._z)**2 )**0.5
            #TODO: Filament object
            self.e = self.e + self.extrusion_multiplier*(self._machine.nozzle_d*distance*0.2)/(math.pi*(1.75/2)**2)
            comment = f"Push {self.extrusion_multiplier*(self._machine.nozzle_d*distance*0.2)/(math.pi*(1.75/2)**2):.4f}mm of filament"
        super().goto(x, y, z, self.e, comment)
