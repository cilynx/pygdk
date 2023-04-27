#!/usr/bin/env python3

from pygdk import FDMPrinter
kossel = FDMPrinter('kossel.json')

kossel.load_filament()

# kossel.print_gcode()
# kossel.simulate()
kossel.OctoPrint(start=True)
