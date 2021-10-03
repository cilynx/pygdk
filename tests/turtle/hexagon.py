#!/usr/bin/env python3

from pygdk import Machine

onefinity = Machine('onefinity.json', safe_z=1)
onefinity.current_tool = '1/16" Upcut'
onefinity.feed = 500

polygon = onefinity.turtle(z=-1)

num_sides = 6
side_length = 70
angle = 360.0 / num_sides

polygon.pendown() 
for i in range(num_sides):
    polygon.forward(side_length)
    polygon.right(angle)
polygon.penup()
