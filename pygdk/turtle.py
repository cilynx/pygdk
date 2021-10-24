import math

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
        self._heading = [1,0,0]
        self._normal = [0,0,1]
        self._right = [0,-1,0]
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
        x = self._x + distance * self.heading()[0]
        y = self._y + distance * self.heading()[1]
        if dz: # 2.5D motion
            if self.heading()[2] == 0:
                z = self._z + dz
            else:
                raise ValueError(f"{RED}You can only use 2.5D motion in the XY-plane")
        else: # 3D motion
            z = self._z + distance * self.heading()[2]
        if self._verbose and comment is None:
            comment = f"Moving at {[round(i,4) for i in self.heading()]} from ({self._x:.4f}, {self._y:.4f}, {self._z:.4f}) to ({x:.4f}, {y:.4f}, {z:.4f})"
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

    def back(self, distance):
        self.forward(-distance)

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
        self._right = self.dot([self._right], self.rot(self._heading, angle))[0]
        self._normal = self.dot([self._normal], self.rot(self._heading, angle))[0]

################################################################################
# Turtle.pitch - Tilt up or down without changing the side vector
################################################################################

    def pitch(self, angle):
        angle = -math.radians(angle)
        self._heading = self.dot([self._heading], self.rot(self._right, angle))[0]
        self._normal = self.dot([self._normal], self.rot(self._right, angle))[0]

################################################################################
# Turtle.yaw - Rotate right or left as viewed from above without changing the
# normal vector
################################################################################

    def yaw(self, angle):
        angle = math.radians(angle)
        self._heading = self.dot([self._heading], self.rot(self._normal, angle))[0]
        self._right = self.dot([self._right], self.rot(self._normal, angle))[0]

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
# Turtle.setheading(to_angle)
# Turtle.seth(to_angle)
#
# Set the orientation of the turtle to to_angle. Here are some common directions
# in degrees:
#
# Standard Mode     Logo Mode
# 0   - East        0   - North
# 90  - North       90  - East
# 180 - West        180 - South
# 270 - South       270 - West
################################################################################

    # def setheading(self, yaw):
    #     self.yaw = 450-yaw if self._mode == "logo" else angle
    #
    # seth = setheading

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
        self._heading = [1,0,0]
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
# Turtle.heading()
#
# Return the turtle’s current heading (value depends on the turtle mode,
# see mode()).
################################################################################

    def heading(self):
        return self._heading

################################################################################
# Turtle.pendown()
# Turtle.pd()
# Turtle.down()
#
# Pull the pen down -- drawing / cutting when moving
################################################################################

    def pendown(self, z=None):
        self._isdown = True
        self._machine.linear_interpolation(z=self._z_draw, comment="Pendown" if self._verbose else None)
        self._z = z if z is not None else self._z_draw

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

    def pencolor(self, color=None):
        if color is not None:
            self._machine.pen_color = color
            self._pencolor = color
        self._machine.rapid(self._x, self._y, comment="Going back to Turtle's (x,y) after color change")
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

    def pendown(self):
        self.e += self.printer.retract_f + self.printer.extra_push
        self.goto(e=self.e, comment="Reprime filament")
        self.extrude = True
        self._isdown = True

    def pencolor(self):
        self.queue(comment="Pen colors are disabled for Squirtle.  Maybe someday I'll play with multiple extruders.", style='warning')

    def forward(self, distance, dz=0, comment=None):
        if self.extrude:
            #TODO: Filament object
            self.e = self.e + self.extrusion_multiplier*(self._machine.nozzle_d*distance*0.2)/(math.pi*(1.75/2)**2)
            comment = f"Pumping {self.extrusion_multiplier*(self._machine.nozzle_d*distance*0.2)/(math.pi*(1.75/2)**2):.4f}mm of filament"
        super().forward(distance, dz, self.e, comment)
