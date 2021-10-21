#!/usr/bin/env python3
from pygdk import Plotter

onefinity = Plotter('onefinity.json', safe_z=-120)
onefinity.feed = 5000

turtle = onefinity.turtle(verbose=True, z=-124)

turtle.goto(725,110)
scale = 0.25
turtle._isdown = True
colors = ['Black', 'Blue', 'Light Blue', 'Red', 'Orange', 'Lime']
for x in range(360):
    turtle.pencolor(colors[x%6])
    turtle.forward(x*scale)
    turtle.left(59.8)

onefinity.pen_color = None
onefinity.print_gcode()
