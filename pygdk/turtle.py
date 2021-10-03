import math

RED  = '\033[31m' # Red
YELLOW = '\033[93m' # Yellow
ENDC  = '\033[0m'  # End Color

class Turtle:

################################################################################
# Turtle.__init__() -- Initializer
################################################################################

    def __init__(self, machine, x=0, y=0, z=0, mode='standard', verbose=False):
        self._verbose = verbose
        self._machine = machine
        self._isdown = False
        self._mode = mode
        self._cut = False
        self._yaw = 0
        self._x = x
        self._y = y
        self._z = z
        print(f";{YELLOW} Initializing Turtle Mode{ENDC}") if self._verbose else None
        machine.retract()

################################################################################
# Turtle.forward(distance)
# Turtle.fd(distance)
#
# Move the turtle forward by the specified distance, in the direction the turtle
# is headed.
################################################################################

    def forward(self, distance):
        x = self._x + distance * math.cos(math.radians(self._yaw))
        y = self._y + distance * math.sin(math.radians(self._yaw))
        comment = f"Moving at {self._y:.4f}-deg from ({self._x:.4f}, {self._y:.4f}) to ({x:.4f}, {y:.4f})" if self._verbose else None
        self.goto(x, y, comment=comment)

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
# Turtle.right(angle)
# Turtle.rt(angle)
#
# Turn turtle right by angle units. (Units are by default degrees, but can be
# set via the degrees() and radians() functions.) Angle orientation depends on
# the turtle mode, see mode().
################################################################################

    def right(self, angle):
        self._yaw -= angle

    rt = right

################################################################################
# Turtle.left(angle)
# Turtle.lt(angle)
#
# Turn turtle left by angle units. (Units are by default degrees, but can be set
# via the degrees() and radians() functions.) Angle orientation depends on the
# turtle mode, see mode().
################################################################################

    def left(self, angle):
        self._yaw += angle

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

    def goto(self, x, y=None, comment=None):
        if self.pos() != [x,y] and self.pos() != x:
            if y is None:
                self._x = x[0]
                self._y = x[1]
            else:
                self._x = x
                self._y = y
            self._machine.move(self._x, self._y, cut=self._isdown, comment=comment)

    setpos = goto
    setposition = goto

################################################################################
# Turtle.setx(x)
#
# Set the turtle’s first coordinate to x, leave second coordinate unchanged.
# If the pen is down, draw line.
################################################################################

    def setx(self, x):
        goto(x, self._y)

################################################################################
# Turtle.sety(y) -- Teleport the Turtle to a new Y-position
#
# Set the turtle’s second coordinate to y, leave first coordinate unchanged.
# If the pen is down, draw line.
################################################################################

    def sety(self, y):
        goto(self._x, y)

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

    def setheading(self, angle):
        self._yaw = (450-angle)%360 if self._mode == "logo" else angle

    seth = setheading

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
            self.pendown
        self._yaw = 0 if self._mode == "logo" else -90

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

    def circle(self, radius, extent=360, steps=None):
        c_x = self._x - radius * math.sin(math.radians(self._yaw))
        c_y = self._y + radius * math.cos(math.radians(self._yaw))
        if steps:
            if radius < 0:
                extent = -extent
            segment = extent/steps
            for i in range(1,steps+1):
                x = c_x + radius * math.sin(math.radians(i*segment+self._yaw))
                y = c_y - radius * math.cos(math.radians(i*segment+self._yaw))
                comment = f"Circle segment {i} of {steps}" if self._verbose else None
                self.goto(x,y,comment=comment)
        self._yaw += extent

################################################################################
# Turtle.speed(speed=None)
#
# Deliberately not implemented.  You want to set your feeds and speeds outside
# of the Turtle framework.  Turtle shouldn't care what you're cutting or drawing
# on or with.
################################################################################

    def speed(self, speed=None):
        print(f";{RED} Turtle.speed() is deliberately not implemented.{ENDC}")
        print(f";{RED} You want to set your feeds and speeds outside of the Turtle framework.{ENDC}")
        print(f";{RED} Turtle shouldn't care what you're cutting or drawing on or with.{ENDC}")

################################################################################
# Turtle.position()
# Turtle.pos()
#
# Return the turtle’s current location (x,y) (as a Vec2D vector).
################################################################################

    def position(self):
        return [self._x, self._y]

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
        return (450-self._yaw)%360 if self._mode == 'logo' else self._yaw

################################################################################
# Turtle.pendown()
# Turtle.pd()
# Turtle.down()
#
# Pull the pen down -- drawing / cutting when moving
################################################################################

    def pendown(self):
        self._isdown = True
        self._machine.cut(z=self._z)

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
        self._machine.retract()

    pu = penup
    up = penup

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