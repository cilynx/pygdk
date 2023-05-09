#!/usr/bin/env python3
from pygdk import Plotter

onefinity = Plotter('onefinity.json')
onefinity.feed = 10000

turtle = onefinity.turtle(z_draw=-126)
turtle.goto(100,100)

colors = ["Black","Red","Blue","Orange","Turquoise","Light Blue","Lime"]

y_pos = 100
for color in colors:
    turtle.pencolor(color)
    x_pos = 100
    for stepover in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        turtle.rectangle(height=20, width=20, start=[x_pos, y_pos+15], stepover=stepover)
        turtle.write(stepover, start=[x_pos+2, y_pos])
        x_pos += 50
    y_pos += 40
    turtle.goto(700,100)

onefinity.go()
