#!/usr/bin/env python3

from pygdk import FDMPrinter

kossel = FDMPrinter('kossel.json')

kossel.set_bed_temp(60)
kossel.wait_for_nozzle_temp(220)
kossel.fan_on()

layer = 0.2
width = 100
depth = 10
tier = 20

squirtle = kossel.squirtle(verbose=True)

squirtle.goto(width/2, depth/2, layer)

squirtle.pendown()
for i in range(int(tier/layer)+5):
    if i == tier/layer:
        kossel.feed = 2000
        squirtle.goto(x=3*width/8, y=squirtle._y-tier)
        squirtle.goto(x=width/4, y=squirtle._y+tier+1)
        squirtle.goto(x=width/8, y=squirtle._y-tier-1)
        squirtle.goto(x=0, y=squirtle._y+tier+1)
        squirtle.goto(x=-width/8, y=squirtle._y-tier-1)
        squirtle.goto(x=-width/4, y=squirtle._y+tier+1)
        squirtle.goto(x=-3*width/8, y=squirtle._y-tier-1)
        squirtle.goto(x=-width/2, y=squirtle._y+tier)
        squirtle.penup()
        squirtle.goto(y=+depth/2)
        squirtle.goto(x=width/2)
        squirtle.goto(y=-depth/2)
        squirtle.pendown()
    kossel.feed = 5000
    squirtle.goto(x=-width/2)
    squirtle.goto(y=+depth/2)
    squirtle.goto(x=width/2)
    squirtle.goto(y=-depth/2, z=squirtle._z+layer)

kossel.go()
