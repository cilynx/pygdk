#!/usr/bin/env python3

from pygdk import FDMPrinter
kossel = FDMPrinter('kossel.json')
kossel.bed_temp(50, block=False)
kossel.nozzle_temp(220, block=True)

squirtle = kossel.squirtle(verbose=True)
squirtle.extrusion_multiplier = 1

def square():
    squirtle.pendown()
    for i in range(int(10/0.4)):
        squirtle.forward(20, comment="prime")
        squirtle.circle(0.2,180, comment="circle back")
        squirtle.forward(20, comment="prime")
        squirtle.circle(-0.2,180, comment="circle_back")
    squirtle.pitch(90)
    squirtle.forward(0.2)
    squirtle.pitch(90)
    squirtle.roll(180)
    squirtle.left(90)
    for i in range(int(10/0.4)):
        squirtle.forward(20, comment="prime")
        squirtle.circle(0.2,180, comment="circle back")
        squirtle.forward(20, comment="prime")
        squirtle.circle(-0.2,180, comment="circle_back")
    squirtle.left(90)
    squirtle.penup()

# Prime the nozzle
squirtle.goto(0, -100, 0.2)
squirtle.pendown()
squirtle.circle(100,180)
squirtle.penup()

# Go back home in preparation to print
squirtle.goto(0,0,0.2)
square()

squirtle.goto(30,0,0.2)
square()

squirtle.goto(0,30,0.2)
square()

squirtle.goto(30,30,0.2)
square()

kossel.print_gcode()
kossel.octoprint()
