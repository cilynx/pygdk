#!/usr/bin/env python3

def test_example_twist(capsys):
    from pygdk import Plotter

    onefinity = Plotter('onefinity.json', safe_z=-120)
    onefinity.feed = 5000

    turtle = onefinity.turtle(z=-124, verbose=True)

    c_x = 725
    c_y = 125
    turtle.goto(c_x, c_y)

    turtle._isdown = True
    turtle.pencolor("Lime")
    scale = 0.5
    for i in range(180):
        turtle.forward(100*scale)
        turtle.right(30)
        turtle.forward(20*scale)
        turtle.left(60)
        turtle.forward(50*scale)
        turtle.right(30)

        turtle.penup()
        turtle.setposition(c_x, c_y)
        turtle.pendown()

        turtle.right(2)

    onefinity.pen_color = None

    del turtle
    [out,err] = capsys.readouterr()
    with open('tests/test_examples/test_twist.nc') as known_good_output:
        assert out == known_good_output.read()
