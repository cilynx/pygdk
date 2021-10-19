#!/usr/bin/env python3

from pygdk import Mill
onefinity = Mill('onefinity.json')
onefinity.tool = '1/4" Downcut'
onefinity.material = 'Hard Wood'

inch = 25.4

hanger_diameter = 3/4*inch
board_diameter = 12*inch
board_circumfrence = board_diameter * 3.14159
handle_length = board_diameter/4
handle_width = handle_length/2
attachment_angle = 90-360*handle_width/board_circumfrence/2
board_angle = 360*(board_circumfrence-handle_width)/board_circumfrence
thickness = 10
segments = 100

# Hanger
onefinity.helix(c_x=handle_length, c_y=handle_width/2, depth=thickness, diameter=hanger_diameter, z_step=1/4*inch)
onefinity.rapid(0,0)

# Board
turtle = onefinity.turtle(verbose=True)
turtle.pendown()
turtle.forward(handle_length, dz=-thickness)
turtle.circle(handle_width/2, 180,segments)
turtle.forward(handle_length)
turtle.right(attachment_angle)
turtle.circle(board_diameter/2, board_angle, segments)
turtle.right(attachment_angle)
turtle.forward(handle_length)
turtle.penup()

