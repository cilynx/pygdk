#!/usr/bin/env python3
from pygdk import Plotter

onefinity = Plotter('onefinity.json')
onefinity.feed = 500
onefinity.tool = '1/8" Downcut, 2 Flutes, 1/4" Shank, Carbide'

turtle = onefinity.turtle(z=-1)

num_sides = 4
angle = 360.0 / num_sides + 2

passes = 100

turtle.pendown()
for i in range(passes * num_sides):
    turtle.forward(i/10)
    turtle.right(angle)
turtle.penup()

onefinity.print_gcode()
onefinity.simulate()
