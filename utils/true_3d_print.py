#!/usr/bin/env python3

from pygdk import FDMPrinter

kossel = FDMPrinter('kossel.json')

kossel.material = 'Amazon Basics Black PLA'
kossel.nozzle = 0.4
kossel.feed = 1000

de = 3*(0.4*10*0.2)/(3.14159*(1.75/2)**2)
e = 0

turtle = kossel.turtle(verbose=True)
turtle.goto(-5, 5, 0.2)
turtle.pendown()
for i in range(10):
    e += de
    turtle.forward(30, e=e, comment="prime")
    e += de
    turtle.circle(0.5,180, e=e, comment="circle back")
    e += de
    turtle.forward(30, e=e, comment="prime")
    e += de
    turtle.circle(-0.5,180, e=e, comment="circle_back")
turtle.penup()
turtle.goto(z=0.5)
turtle.goto(0,0,0.2)
turtle.pendown()

for i in range(50):
    for j in range(4):
        e += de
        turtle.forward(10, dz=0.2/4, e=e, comment="post")
        turtle.right(90)

for j in range(21):
    for i in range(4):
        e += de
        turtle.forward(10, e=e, comment="curve")
        turtle.right(90)
    turtle.roll(1)

for i in range(100):
    for i in range(4):
        e += de
        turtle.forward(10, e=e, comment="bridge")
        turtle.right(90)
    turtle.roll(-20)
    turtle.left(90)
    e += de
    turtle.forward(0.2, e=e, comment="layer")
    turtle.right(90)
    turtle.roll(20)

e += de
turtle.forward(10, e=e, comment="changeup")
turtle.right(90)
e += de
turtle.forward(10, e=e, comment="changeup")
turtle.right(90)

for j in range(21):
    for i in range(4):
        e += de
        turtle.forward(10, e=e, comment="curve")
        turtle.right(90)
    turtle.roll(1)

for i in range(50):
    for j in range(4):
        e += de
        turtle.forward(10, e=e, dz=0.2/4, comment="post")
        turtle.right(90)
