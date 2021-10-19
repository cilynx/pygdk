#!/usr/bin/env python3

from pygdk import FDMPrinter
kossel = FDMPrinter('kossel.json')
kossel.bed_temp(50, block=False)
kossel.nozzle_temp(220, block=True)

squirtle = kossel.squirtle(verbose=True)
squirtle.extrusion_multiplier = 1

# Prime the nozzle
squirtle.goto(0, -100, 0.2)
squirtle.pendown()
squirtle.circle(100,180)
squirtle.penup()

# Go back home in preparation to print
squirtle.goto(0,0,0.2)

squirtle.pendown()
for i in range(int(20/0.2)):
    for j in range(4):
        squirtle.forward(20)
        squirtle.right(90)
    squirtle.pitch(90)
    squirtle.forward(0.2)
    squirtle.pitch(-90)
