#!/usr/bin/env python3

import math

def sin(x):
    return math.sin(math.radians(x))

def cos(x):
    return math.cos(math.radians(x))

from pygdk import FDMPrinter

kossel = FDMPrinter('kossel.json')

kossel.set_bed_temp(60)
kossel.wait_for_nozzle_temp(210)
kossel.fan_on()

squirtle = kossel.squirtle(verbose=True)
squirtle.penup()

layer = 0.2
pillar_d = 20
height = 20
table_d = 80

pillar_c = 3.14159 * pillar_d
step = pillar_c / 360

squirtle.goto(0, pillar_d, layer)
squirtle.heading = [1,0,0]

squirtle.pendown()


kossel.feed = 500
while(squirtle._z < height):
    for i in range(360):
        if kossel.feed < 1400:
            kossel.feed += 1
        squirtle.forward(step, dz=layer/360)
        squirtle.right(1)

i = 0
kossel.feed = 200
while(squirtle._y < table_d/2):
    for _ in range(360):
        i += 0.000015
        squirtle.forward(step+i)
        squirtle.right(1)

kossel.go()
