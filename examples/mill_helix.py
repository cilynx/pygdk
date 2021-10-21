#!/usr/bin/python

from pygdk import Mill

onefinity = Mill('onefinity.json')
onefinity.tool = '1/4" Downcut'
onefinity.material = 'Soft Wood'

onefinity.helix(0,0,10,10)
onefinity.print()
