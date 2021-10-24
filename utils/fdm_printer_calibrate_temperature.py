#!/usr/bin/env python3

from pygdk import FDMPrinter

kossel = FDMPrinter('kossel.json')

kossel.bed_temp = 50
kossel.nozzle_temp = 180
kossel.feed = 2000
kossel.max_feed = 7000

layer = 0.2

turtle = kossel.squirtle(verbose=True)
turtle.goto(0,0,layer)
turtle.penup()
turtle.forward(110)
turtle.left(90)
turtle.pendown()
turtle.circle(110)
turtle.left(90)
turtle.forward(110)
turtle.left(180)
turtle.penup()

for j in range(4):
    turtle.goto(0,0,100)
    kossel.nozzle_temp += 10
    turtle.goto(45-40*j, -5, layer)
    kossel.feed = 1000
    turtle.pendown()
    for i in range(30):
        turtle.forward(30, comment="prime")
        turtle.circle(-0.5,180, comment="circle back")
        kossel.feed += 100
        turtle.forward(30, comment="prime")
        turtle.circle(0.5,180, comment="circle_back")
        kossel.feed += 100
    turtle.penup()

for j in range(4):
    turtle.goto(0,0,100)
    kossel.nozzle_temp += 10
    turtle.goto(45-40*j, 5, layer)
    kossel.feed = 1000
    turtle.pendown()
    for i in range(30):
        turtle.forward(30, comment="prime")
        turtle.circle(0.5,180, comment="circle back")
        kossel.feed += 100
        turtle.forward(30, comment="prime")
        turtle.circle(-0.5,180, comment="circle_back")
        kossel.feed += 100
    turtle.penup()


kossel.print_gcode()
kossel.OctoPrint(True)
#kossel.CAMotics()

# turtle.penup()
# turtle.goto(z=2)
# turtle.goto(-40,-40,layer)
# turtle.left(90)
# turtle.pendown()
#
# for i in range(50):
#     kossel.feed += 250
#     for j in range(4):
#         turtle.forward(80, dz=layer/4, comment="post")
#         turtle.circle(-10, 90)

# for j in range(21):
#     for i in range(4):
#         turtle.forward(10, comment="curve")
#         turtle.right(90)
#     turtle.roll(1)
#
# for i in range(100):
#     for i in range(4):
#         turtle.forward(10, comment="bridge")
#         turtle.right(90)
#     turtle.roll(-20)
#     turtle.left(90)
#     turtle.forward(layer, comment="layer")
#     turtle.right(90)
#     turtle.roll(20)
#
# turtle.forward(10, comment="changeup")
# turtle.right(90)
# turtle.forward(10, comment="changeup")
# turtle.right(90)
#
# for j in range(21):
#     for i in range(4):
#         turtle.forward(10, comment="curve")
#         turtle.right(90)
#     turtle.roll(1)
#
# for i in range(50):
#     for j in range(4):
#         turtle.forward(10, dz=layer/4, comment="post")
#         turtle.right(90)
#
# kossel.print_gcode()
# kossel.OctoPrint()
# #kossel.save_gcode()
# #kossel.CAMotics()
