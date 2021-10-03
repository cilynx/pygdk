#!/usr/bin/env python3

from pygdk import Machine

onefinity = Machine('onefinity.json')
onefinity.current_tool = '1/8'
onefinity.feed = 500

t = onefinity.turtle(z=-1, verbose=True)

t.pendown()
t.left(90)

def branch(iteration, branchLength, angle):
  if iteration == 0:
    return
  t.forward(branchLength)
  t.left(angle)
  branch(iteration-1, branchLength/1.5, angle)
  t.right(angle)
  t.right(angle)
  branch(iteration-1, branchLength/1.5, angle)
  t.left(angle)
  t.back(branchLength)

branch(7, 50, 30)
