#!/usr/bin/env python3

from pygdk import FDMPrinter
kossel = FDMPrinter('kossel.json')

kossel.wait_for_bed = False
kossel.bed_temp = 60
kossel.wait_for_nozzle = True
kossel.nozzle_temp = 220

kossel.feed = 5000
kossel.fan_on()

squirtle = kossel.squirtle(verbose=True)

squirtle.goto(0, 0, 0.2)

squirtle.pendown(prime=False)

import math

def x(t):
    return 16*math.sin(t)**3

def y(t):
    return 13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)

for j in range(2, 200, 4):
    j = j/10
    for i in range(3, 61):
        if i not in (29, 31, 32, 33, 34): # Too many spindles at the point
            squirtle.goto(z=j)
            squirtle.goto(4*x(i/10), 4*y(i/10))
            squirtle.goto(z=j+0.2)
            squirtle.goto(0, 0)

kossel.fan_off()

kossel.go()
