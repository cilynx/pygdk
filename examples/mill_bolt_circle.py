#!/usr/bin/env python3

from pygdk import Mill

onefinity = Mill('onefinity.json')
onefinity.material = 'Soft Wood'
onefinity.tool = '1/4" Downcut'

onefinity.bolt_circle(0, 0, 8, 10, -10)

onefinity.simulate()
