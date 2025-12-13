#!/usr/bin/env python3

from pygdk import FDMPrinter

kossel = FDMPrinter('kossel.json')

kossel.set_bed_temp(60)
kossel.wait_for_nozzle_temp(200)

kossel.fan_on()

side = 25

squirtle = kossel.squirtle()

squirtle.penup()
# squirtle.goto(50, 0)
#
# kossel.feed = 500
# squirtle.pendown()
# for i in range(int(10/0.2)):
#     if kossel.feed < 2000:
#         kossel.feed += 100
#     squirtle.pitch(90)
#     squirtle.forward(0.2)
#     squirtle.pitch(-90)
#     for j in range(4):
#         squirtle.forward(side)
#         squirtle.right(90)
#
#
# squirtle.penup()
# squirtle.goto(-100, 0, 0.2)
#
# kossel.feed = 500
# squirtle.pendown()
# for i in range(int(30/0.2)):
#     if kossel.feed < 2000:
#         kossel.feed += 100
#     squirtle.pitch(90)
#     squirtle.forward(0.2)
#     squirtle.pitch(-90)
#     for j in range(4):
#         squirtle.forward(side)
#         squirtle.right(90)

kossel.feed = 2000
squirtle.goto(x=side-100, y=0, z=30)
squirtle.pendown()

for _ in range(side*2):
    squirtle.goto(x=50.5, z=10)
    kossel.feed = 500
    squirtle.goto(y=squirtle._y-0.5)
    kossel.feed = 2000
    squirtle.goto(x=side-100.5, z=30)

squirtle.penup()
squirtle.goto(0,0,200)

kossel.go()
