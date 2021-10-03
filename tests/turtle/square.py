#!/usr/bin/env python3

from pygdk import Machine

onefinity = Machine('onefinity.json')
onefinity.select_tool('1/16" Upcut')

skk = onefinity.turtle()

for i in range(4):
    skk.forward(50)
    skk.right(90)
