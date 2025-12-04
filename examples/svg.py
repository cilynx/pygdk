#!/usr/bin/env python

from pygdk import Plotter

plotter = Plotter("onefinity.json")
plotter.feed = 6000

#plotter.draw("alpaca.svg", pen="Black")
plotter.draw("corgi.svg", origin=(100,100), scale=0.25)
plotter.print_gcode()
plotter.simulate()
