#!/usr/bin/env python3

from pygdk import FDMPrinter

kossel = FDMPrinter('kossel.json')

kossel.material = 'Amazon Basics Black PLA'
kossel.feed = 1000

kossel.wait_for_bed = False
kossel.bed_temp = 60
kossel.wait_for_nozzle = True
kossel.nozzle_temp = 200
kossel.wait_for_bed = True
kossel.bed_temp = 60

squirtle = kossel.squirtle(verbose=True)
squirtle.goto(-5, 5, 0.2)
squirtle.pendown()

# Priming grid
for i in range(10):
    squirtle.forward(30, comment="prime")
    squirtle.circle(0.5,180, comment="circle back")
    squirtle.forward(30, comment="prime")
    squirtle.circle(-0.5,180, comment="circle_back")
squirtle.penup()
squirtle.goto(z=0.5)
squirtle.goto(0,0,0.2)
squirtle.pendown()

# Lower post
for i in range(20):
    for j in range(4):
        squirtle.forward(20, dz=0.2/4, comment="post")
        squirtle.right(90)

# Lower elbow
for j in range(21):
    for i in range(4):
        squirtle.forward(20, comment="curve")
        squirtle.right(90)
    squirtle.roll(1)

# Horizontal bridge
for i in range(120):
    for i in range(4):
        squirtle.forward(20, comment="bridge")
        squirtle.right(90)
    squirtle.roll(-20)
    squirtle.left(90)
    squirtle.forward(0.2, comment="layer")
    squirtle.right(90)
    squirtle.roll(20)

squirtle.forward(20, comment="changeup")
squirtle.right(90)
squirtle.forward(20, comment="changeup")
squirtle.right(90)

# Upper elbow
for j in range(21):
    for i in range(4):
        squirtle.forward(20, comment="curve")
        squirtle.right(90)
    squirtle.roll(1)

# Upper post
for i in range(20):
    for j in range(4):
        squirtle.forward(20, dz=0.2/4, comment="post")
        squirtle.right(90)

kossel.print_gcode()
#kossel.simulate()
#kossel.send_gcode()
kossel.octoprint(True)
