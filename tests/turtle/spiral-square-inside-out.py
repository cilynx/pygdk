#!/usr/bin/env python3

from pygdk import Machine

onefinity = Machine('onefinity.json', safe_z=-120)
onefinity.feed = 5000

skk = onefinity.turtle(verbose=True, z=-124)

colors = ["Black","Red","Blue","Green"]
import random

skk.goto(725,110)

skk._isdown = True
def sqrfunc(size):
    for i in range(4):
        skk.pencolor(colors[i%4])
        skk.fd(size)
        skk.left(90)
        size = size + 5

sqrfunc(6)
sqrfunc(26)
sqrfunc(46)
sqrfunc(66)
sqrfunc(86)
sqrfunc(106)
sqrfunc(126)
sqrfunc(146)

onefinity.pen_color = None
