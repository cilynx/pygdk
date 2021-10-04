#!/usr/bin/env python3

from pygdk import Machine

onefinity = Machine('onefinity.json', safe_z=-120)
onefinity.feed = 5000

t = onefinity.turtle(verbose=True, z=-124)

t.goto(725,110)
scale = 0.25
t._isdown = True
colors = ['Black', 'Blue', 'Light Blue', 'Turquoise', 'Green', 'Lime']
for x in range(360):
    t.pencolor(colors[x%6])
#    t.width(x//100 + 1)
    t.forward(x*scale)
    t.left(59.8)

onefinity.pen_color = None
