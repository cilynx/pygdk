#!/usr/bin/env python3

from pygdk import FDMPrinter
kossel = FDMPrinter('kossel.json')
kossel.bed_temp(50, block=False)
kossel.nozzle_temp(220, block=True)
kossel.bed_temp(50, block=True)

kossel.feed = 4000

squirtle = kossel.squirtle(verbose=True)
squirtle.extrusion_multiplier = 1

squirtle.goto(z=0.2)
squirtle.pendown()
for i in range(10):
    squirtle.forward(60, comment="prime")
    squirtle.circle(0.2,180, comment="circle back")
#    squirtle.extrusion_multiplier += 0.5
    squirtle.forward(60, comment="prime")
    squirtle.circle(-0.2,180, comment="circle_back")
#    squirtle.extrusion_multiplier += 0.5
