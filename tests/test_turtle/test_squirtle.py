from pygdk.turtle import Squirtle, Turtle
from pygdk.fdm_printer import FDMPrinter
kossel = FDMPrinter('kossel.json')

def test_squirtle_successful_init():
    squirtle = kossel.squirtle()
    assert isinstance(squirtle, Squirtle)
    assert isinstance(squirtle, Turtle)
    assert squirtle.position() == [0,0,0]
    assert squirtle.extrusion_multiplier == 1
    assert squirtle.extrude == False

def test_squirtle_extrude_false():
    squirtle = kossel.squirtle()
    squirtle.forward(10)
    assert squirtle.e == 0

def test_squirtle_extrude_true():
    squirtle = kossel.squirtle()
    squirtle.extrude = True
    squirtle.forward(10)
    assert squirtle.e != 0

def test_squirtle_penupdown():
    squirtle = kossel.squirtle()
    assert squirtle.extrude == False
    squirtle.forward(10)
    assert squirtle.e == 0
    squirtle.pendown()
    assert squirtle.extrude == True
    squirtle.forward(10)
    assert squirtle.e != 0
    e = squirtle.e
    squirtle.penup()
    assert squirtle.extrude == False
    squirtle.forward(10)
    assert squirtle.e == e-squirtle._machine.retract_f
