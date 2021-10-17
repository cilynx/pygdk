#!/usr/bin/env python3

def test_example_turtle_circles(capsys):
    from pygdk import Plotter

    onefinity = Plotter('onefinity.json')
    onefinity.feed = 500

    turtle = onefinity.turtle(z=-1, verbose=True)

    turtle.pendown()

    count = 5
    segment = 360/count
    for i in range(count):
        turtle.left(segment)
        turtle.circle(10, steps=100)

    del turtle
    [out,err] = capsys.readouterr()
    with open('tests/test_examples/test_turtle_circles.nc') as known_good_output:
        assert out == known_good_output.read()
