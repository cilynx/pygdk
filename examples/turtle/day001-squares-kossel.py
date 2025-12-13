#!/usr/bin/env python3

from pygdk import FDMPrinter
kossel = FDMPrinter('kossel.json')

kossel.wait_for_bed = False
kossel.bed_temp = 50
kossel.wait_for_nozzle = True
kossel.nozzle_temp = 220
kossel.wait_for_bed = True
kossel.bed_temp = 50

squirtle = kossel.squirtle(verbose=True)
squirtle.extrusion_multiplier = 1

#turtle = kossel.turtle(verbose=True)

squirtle.goto(0, 0, 0.2)

squirtle.pendown()

for i in range(100):
        squirtle.forward(i)
        squirtle.left(90)

#kossel.print_gcode()
kossel.go()
