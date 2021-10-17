#!/usr/bin/env python3

def test_example_turtle_hexagon(capsys):
    from pygdk import Plotter

    onefinity = Plotter('onefinity.json')
    onefinity.feed = 500

    turtle = onefinity.turtle(z=-1)

    num_sides = 6
    side_length = 70
    angle = 360.0 / num_sides

    turtle.pendown()
    for i in range(num_sides):
        turtle.forward(side_length)
        turtle.right(angle)
    turtle.penup()

    del turtle
    [out,err] = capsys.readouterr()
    with open('tests/test_examples/test_turtle_hexagon.nc') as known_good_output:
        assert out == known_good_output.read()
