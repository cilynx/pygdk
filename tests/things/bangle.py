#!/usr/bin/env python3

from pygdk import Machine

onefinity = Machine('onefinity.json')

onefinity.material = 'Soft Wood'

onefinity.tool = '1/4" Downcut'

onefinity.helix(c_x=0, c_y=0, diameter=67, depth=21, z_step=10)

onefinity.helix(c_x=0, c_y=0, diameter=77, depth=21, z_step=10, outside=True)
