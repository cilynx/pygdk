#!/usr/bin/python

from pygdk import Mill

onefinity = Mill('onefinity.json')
onefinity.tool = '1/4" Downcut'
onefinity.material = 'Soft Wood'

onefinity.circular_pocket(0,0,15,10)
onefinity.print()
