#!/usr/bin/env python3

def test_example_turtle_tree(capsys):
    from pygdk import Plotter

    onefinity = Plotter('onefinity.json')
    onefinity.feed = 500

    turtle = onefinity.turtle(z=-1, verbose=True)

    turtle.pendown()
    turtle.left(90)

    def branch(iteration, branchLength, angle):
      if iteration == 0:
        return
      turtle.forward(branchLength)
      turtle.left(angle)
      branch(iteration-1, branchLength/1.5, angle)
      turtle.right(angle)
      turtle.right(angle)
      branch(iteration-1, branchLength/1.5, angle)
      turtle.left(angle)
      turtle.back(branchLength)

    branch(7, 50, 30)

    del turtle
    [out,err] = capsys.readouterr()
    with open('tests/test_examples/test_turtle_tree.nc') as known_good_output:
        assert out == known_good_output.read()
