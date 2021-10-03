#!/usr/bin/env python3

from pygdk import Machine

onefinity = Machine('onefinity.json')
onefinity.select_tool('1/16" Upcut')

star = onefinity.turtle()

star.right(75)
star.forward(100)

for i in range(4):
  star.right(144)
  star.forward(100)
