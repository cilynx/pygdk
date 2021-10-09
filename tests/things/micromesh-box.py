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

hollow_x = length-2*sidewall-10
hollow_y = width-2*sidewall-10
hollow_z = height-5

onefinity._y_clear = 60

onefinity.select_tool('1/2" Ball End')
# Main Hollow
onefinity.rectangular_pocket(c_x=length/2, c_y=width/2, x=hollow_x, y=hollow_y, depth=hollow_z)

onefinity.select_tool('1/8" Downcut')
# Pad Slots
for i in range(pad_count):
    onefinity.rectangular_pocket(c_x=sidewall+pad_thickness/2+i*(pad_thickness+divider), c_y=width/2, x=pad_thickness, y=pad_width, depth=height-sidewall)

onefinity.select_tool('1/4" Downcut')
# Lip for Lid
onefinity.frame(c_x=length/2, c_y=width/2, x=length-sidewall, y=width-sidewall, depth=5, r=onefinity.current_tool.radius, feature="Lip for lid")
# Outer Perimeter
onefinity.frame(c_x=length/2, c_y=width/2, x=length, y=width, depth=height, feature="Outer Perimiter")

onefinity.full_retract()
