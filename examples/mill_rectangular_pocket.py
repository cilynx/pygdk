#!/usr/bin/python

from pygdk import Mill

onefinity = Mill('onefinity.json')
onefinity.tool = '1/4" Downcut'
onefinity.material = 'Soft Wood'

onefinity.rectangular_pocket(0,0,20,10,z_bottom=-10)
onefinity.print_gcode()
