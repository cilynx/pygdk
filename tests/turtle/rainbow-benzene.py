#!/usr/bin/env python3

from pygdk import Machine

onefinity = Machine('onefinity.json')
onefinity.select_tool('1/16" Upcut')

t = onefinity.turtle()

colors = ['red', 'purple', 'blue', 'green', 'orange', 'yellow']
for x in range(360):
#    t.pencolor(colors[x%6])
#    t.width(x//100 + 1)
    t.forward(x)
    t.left(59.8)
