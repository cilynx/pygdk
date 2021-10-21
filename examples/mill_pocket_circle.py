#!/usr/bin/python

from pygdk import Mill

onefinity = Mill('onefinity.json')
onefinity.tool = '1/4" Downcut'
onefinity.material = 'Soft Wood'

onefinity.pocket_circle(0,0,8,100,10,10, theta=360/16)
onefinity.print_gcode()
