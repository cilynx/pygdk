#!/usr/bin/env python3

# Demo:
# https://youtube.com/shorts/LU13_r0r3Ns

# Inspired by:
# https://github.com/atlemgw/turtlegraphics/blob/master/day1
# https://www.youtube.com/watch?v=6oPapWwdboQ

from pygdk import Plotter

onefinity = Plotter('onefinity.json')
onefinity.feed = 500

turtle = onefinity.turtle(z=-1)

import math

def x(t):
    return 16*math.sin(t)**3

def y(t):
    return 13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)

for i in range(650):
	turtle.pendown()
	turtle.goto(100*x(i/100), 100*y(i/100))
	turtle.penup()
	turtle.goto(0, 0)

onefinity.print_gcode()
onefinity.simulate()
