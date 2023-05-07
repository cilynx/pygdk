#!/usr/bin/env python3
from pygdk import Plotter

onefinity = Plotter('onefinity.json', safe_z=-120)
onefinity.feed = 5000

onefinity._optimize = True

turtle = onefinity.turtle(verbose=True, z_draw=-126)

turtle.goto(725,110,-115)
scale = 0.25
turtle._isdown = True
colors = ['Black', 'Orange', 'Lime', 'Blue', 'Red', 'Light Blue']
for x in range(360):
    turtle._z_draw = onefinity.dict['Plotter']['Z-Touch']
    turtle.pencolor(colors[x%6])
    turtle.forward(x*scale)
    turtle.left(59.8)

onefinity.pen_color = None

onefinity.go()
