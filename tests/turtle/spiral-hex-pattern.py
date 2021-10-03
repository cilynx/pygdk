#!/usr/bin/env python3

from pygdk import Machine

onefinity = Machine('onefinity.json')
onefinity.select_tool('1/16" Upcut')

turtle = onefinity.turtle()

for i in range(100):
    turtle.circle(5*i)
    turtle.circle(-5*i)
    turtle.left(i)
