#!/usr/bin/env python3

from pygdk import Machine

onefinity = Machine('onefinity.json')

onefinity.pen_color = "Black"
onefinity.rapid(x=700, y=100)
onefinity.rapid(z=-123)
onefinity.rapid(y=110)
onefinity.rapid(x=710)
onefinity.rapid(y=100)
onefinity.rapid(x=700)
onefinity.pen_color = "Blue"
onefinity.rapid(x=720, y=100)
onefinity.rapid(z=-123)
onefinity.rapid(y=110)
onefinity.rapid(x=730)
onefinity.rapid(y=100)
onefinity.rapid(x=720)
onefinity.pen_color = "Red"
onefinity.rapid(x=700, y=120)
onefinity.rapid(z=-123)
onefinity.rapid(x=710)
onefinity.rapid(y=130)
onefinity.rapid(x=700)
onefinity.rapid(y=120)
onefinity.pen_color = "Black"
onefinity.rapid(x=730, y=120)
onefinity.rapid(z=-123)
onefinity.rapid(y=130)
onefinity.pen_color = "Light Blue"
onefinity.rapid(x=730, y=130)
onefinity.rapid(z=-123)
onefinity.rapid(x=720)
onefinity.pen_color = "Lime"
onefinity.rapid(x=720, y=130)
onefinity.rapid(z=-123)
onefinity.rapid(y=120)
onefinity.pen_color = "Orange"
onefinity.rapid(x=720, y=120)
onefinity.rapid(z=-123)
onefinity.rapid(x=730)
onefinity.pen_color = None
#onefinity.pen_color = "Green"

#print(onefinity.pen_color)

#rf30 = Machine('rf30.json')

#rf30.select_tool(1)
#rf30.css = 0.9

# c_x, c_y, n, r, d
#rf30.bolt_circle(0, 0, 10, 20)

# c_x, c_y, diameter, depth
#rf30.circular_pocket(0,0,3/4*25.4,5)
#rf30.circular_pocket(30,0,20,5)

# c_x, c_y, n, r, depth, diameter, finish
#rf30.pocket_circle(0, 0, 10, 40, 5, 20)

# c_x, c_y, x, y, depth, finish
#rf30.rectangular_pocket(0,0,40,30,5,undercut=True)
#rf30.rectangular_pocket(50,0,35,35,5,undercut=False)
#rf30.rectangular_pocket(100,0,30,40,5,undercut=True)

# c_x, c_y, big_d, small_d, depth, step, finish, retract
#rf30.keyhole(0,0,10,5,3)
