#!/usr/bin/env python3

from pygdk import Machine

onefinity = Machine('onefinity.json')
onefinity.material = 'Soft Wood'

pad_width = 52
pad_thickness = 5
pad_count = 9
divider = 1
sidewall = 2

width = pad_width + 2*sidewall
length = pad_count*pad_thickness + (pad_count-1)*divider + 2*sidewall
height = pad_width/2

hollow_x = width-2*sidewall-10
hollow_y = length-2*sidewall-10
hollow_z = height-5

onefinity._y_clear = 60

def box(c_x, c_y):
    onefinity.tool = '1/2" Round Nose'
    onefinity.rectangular_pocket(c_x, c_y, x=hollow_x, y=hollow_y, z_bottom=-hollow_z, feature="Main Hollow")

    onefinity.tool = '1/8" Downcut'
    for i in range(pad_count): # Pad Slots
        onefinity.rectangular_pocket(c_x, c_y=sidewall+pad_thickness/2+i*(pad_thickness+divider), x=pad_width, y=pad_thickness, z_bottom=sidewall-height)

    onefinity.tool = '1/4" Downcut'
    onefinity.frame(c_x, c_y, x=width-sidewall, y=length-sidewall, z_bottom=-5, r=onefinity.tool.radius, feature="Lip for lid")

    onefinity.full_retract()

box(width/2, length/2)
box(width+5+width/2, length/2)
onefinity.frame((2*width+5)/2, length/2, x=2*width+10, y=length, z_bottom=-height, feature="Outer Perimiter")
