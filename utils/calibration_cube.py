#!/usr/bin/env python3

from pygdk import FDMPrinter
kossel = FDMPrinter('kossel.json')
kossel.set_bed_temp(50)
kossel.wait_for_nozzle_temp(220)

kossel.fan_on()

try:
    side = float(kossel._args.arg)
except:
    side = 20

print(f"Side: {side}")
exit

side = side-kossel.nozzle_d/2

squirtle = kossel.squirtle(verbose=True)

kossel.feed = 3000

# Prime the nozzle
squirtle.goto(0, -100, 0.2)
squirtle.pendown()
squirtle.circle(100, 180, 360)
squirtle.penup()

# Go back home in preparation to print
squirtle.goto(0,0,0)

kossel.feed = 500

squirtle.pendown()
for i in range(int(side/0.2)+2):
    if kossel.feed < 2500:
        kossel.feed += 100
    squirtle.pitch(90)
    squirtle.forward(0.2)
    squirtle.pitch(-90)
    for j in range(4):
        squirtle.forward(side)
        squirtle.right(90)
