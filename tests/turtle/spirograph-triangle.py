#!/usr/bin/env python3

from pygdk import Machine

onefinity = Machine('onefinity.json')
onefinity.current_tool = '1/8'
onefinity.feed = 500

turtle = onefinity.turtle(z=-1, verbose=True)

step = 100
length = 100
angle = 120    

turtle.speed()
turtle.pendown()

for i in range (0,step):
  for b in range (0,2):
    turtle.forward(length+i*2)
    turtle.right(angle+b)   

turtle.penup()
