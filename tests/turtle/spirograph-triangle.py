#!/usr/bin/env python3

from pygdk import Machine

onefinity = Machine('onefinity.json', safe_z=-120)
onefinity.feed = 5000

turtle = onefinity.turtle(z=-124, verbose=True)

step = 100
length = 30 
angle = 120

turtle.goto(700,120)

turtle._isdown = True
turtle.pencolor("Red")

for i in range (0,step):
  for b in range (0,2):
    turtle.forward(length+i*2)
    turtle.right(angle+b)

turtle.penup()
onefinity.pen_color = None
