#!/usr/bin/env python3
from pygdk import Plotter

onefinity = Plotter('onefinity.json')
onefinity.feed = 500

turtle = onefinity.turtle(z=-1)

num_sides = 6
side_length = 70
angle = 360.0 / num_sides

turtle.pendown()
for i in range(num_sides):
    turtle.forward(side_length)
    turtle.right(angle)
turtle.penup()

onefinity.print_gcode()
