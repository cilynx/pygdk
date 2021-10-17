#!/usr/bin/env python3

def test_example_bangle(capsys):

    from pygdk import Plotter

    onefinity = Plotter('onefinity.json', safe_z=-120)
    onefinity.feed = 5000

    turtle = onefinity.turtle(verbose=True, z=-124)

    turtle.goto(725,110)
    scale = 0.25
    turtle._isdown = True
    colors = ['Black', 'Blue', 'Light Blue', 'Red', 'Orange', 'Lime']
    for x in range(360):
        turtle.pencolor(colors[x%6])
        turtle.forward(x*scale)
        turtle.left(59.8)

    onefinity.pen_color = None

    del turtle
    [out,err] = capsys.readouterr()
    with open('tests/test_examples/test_rainbow_benzene.nc') as known_good_output:
        assert out == known_good_output.read()
