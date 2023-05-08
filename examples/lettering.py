#!/usr/bin/env python3
from pygdk import Plotter

onefinity = Plotter('onefinity.json')
onefinity.feed = 1000

turtle = onefinity.turtle()
turtle.write("3.1415926535859mm")

onefinity.go()
