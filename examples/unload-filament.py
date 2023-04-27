#!/usr/bin/env python3

from pygdk import FDMPrinter
kossel = FDMPrinter('kossel.json')

kossel.unload_filament()

kossel.print_gcode()
# kossel.simulate()
kossel.OctoPrint(start=True)
