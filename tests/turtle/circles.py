#!/usr/bin/env python3

from pygdk import Machine

onefinity = Machine('onefinity.json')
onefinity.current_tool = '1/16" Upcut'
onefinity.feed = 500

turtle = onefinity.turtle(z=-1, verbose=True)

turtle.pendown()

count = 5
segment = 360/count
for i in range(count):
  turtle.left(segment)
  turtle.circle(10, steps=100)
