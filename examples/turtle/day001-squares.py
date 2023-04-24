#!/usr/bin/env python3

# Inspired by: https://www.youtube.com/watch?v=6oPapWwdboQ

from pygdk import Plotter

onefinity = Plotter('onefinity.json')
onefinity.feed = 500

turtle = onefinity.turtle(z=-1)

turtle.pendown()

for i in range(500):
	turtle.forward(i)
	turtle.left(90)

turtle.penup()

onefinity.print_gcode()
onefinity.simulate()
