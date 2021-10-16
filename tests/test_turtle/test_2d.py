from pygdk.machine import Machine
machine = Machine('onefinity.json')

def test_goto():
    turtle = machine.turtle()
    assert turtle.position() == [0,0,0]
    turtle.goto(0,1)
    assert turtle.position() == [0,1,0]
    turtle.goto(1,0)
    assert turtle.pos() == [1,0,0]

def test_setpos():
    turtle = machine.turtle()
    assert turtle.position() == [0,0,0]
    turtle.setpos(0,1)
    assert turtle.position() == [0,1,0]
    turtle.setpos(1,0)
    assert turtle.pos() == [1,0,0]

def test_setposition():
    turtle = machine.turtle()
    assert turtle.position() == [0,0,0]
    turtle.setposition(0,1)
    assert turtle.position() == [0,1,0]
    turtle.setposition(1,0)
    assert turtle.pos() == [1,0,0]

def test_setx():
    turtle = machine.turtle()
    assert turtle.position() == [0,0,0]
    turtle.setx(1)
    assert turtle.position() == [1,0,0]

def test_sety():
    turtle = machine.turtle()
    assert turtle.position() == [0,0,0]
    turtle.sety(1)
    assert turtle.position() == [0,1,0]

def test_forward():
    turtle = machine.turtle()
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.forward(1)
    assert turtle._heading  == [1,0,0]  # Basis should not change
    assert turtle._normal   == [0,0,1]
    assert turtle._right    == [0,-1,0]
    assert turtle.pos()     == [1,0,0]  # Position increments 1 down the +X axis
    turtle.right(90)
    turtle.forward(1)
    assert turtle._heading  == [0,-1,0]
    assert turtle._normal   == [0,0,1]
    assert turtle._right    == [-1,0,0]
    assert turtle.pos()     == [1,-1,0] # Position increments 1 down the -Y axis
    turtle.left(90)
    turtle.forward(-1)
    assert turtle._heading  == [1,0,0]
    assert turtle._normal   == [0,0,1]
    assert turtle._right    == [0,-1,0]
    assert turtle.pos()     == [0,-1,0] # Position decrements 1 down the -Y axis

def test_fd():
    turtle = machine.turtle()
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.fd(1)
    assert turtle._heading  == [1,0,0]  # Basis should not change
    assert turtle._normal   == [0,0,1]
    assert turtle._right    == [0,-1,0]
    assert turtle.pos()     == [1,0,0]  # Position increments 1 down the +X axis
    turtle.right(90)
    turtle.fd(1)
    assert turtle._heading  == [0,-1,0]
    assert turtle._normal   == [0,0,1]
    assert turtle._right    == [-1,0,0]
    assert turtle.pos()     == [1,-1,0] # Position increments 1 down the -Y axis
    turtle.left(90)
    turtle.fd(-1)
    assert turtle._heading  == [1,0,0]
    assert turtle._normal   == [0,0,1]
    assert turtle._right    == [0,-1,0]
    assert turtle.pos()     == [0,-1,0] # Position decrements 1 down the -Y axis

def test_yaw():
    turtle = machine.turtle()
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.yaw(90)
    assert turtle._heading  == [0,-1,0] # Looking down the -Y axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [-1,0,0] # Looking down the -X axis
    assert turtle.pos()     == [0,0,0]
    turtle.yaw(-90)
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.yaw(0)
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.yaw(90+360)
    assert turtle._heading  == [0,-1,0] # Looking down the -Y axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [-1,0,0] # Looking down the -X axis
    assert turtle.pos()     == [0,0,0]
    turtle.yaw(-90-360)
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    for i in range(36000):
        turtle.yaw(1)
    assert turtle._heading  == [1,0,0]
    turtle.yaw(45)
    assert round(turtle._heading[0],12) == round((2**0.5)/2,12)
    assert round(turtle._heading[1],12) == round(-(2**0.5)/2,12)
    assert round(turtle._heading[2],12) == 0
    assert turtle._normal == [0,0,1]  # Normal should always be +Z in 2D
    assert round(turtle._right[0],12) == round(-(2**0.5)/2,12)
    assert round(turtle._right[1],12) == round(-(2**0.5)/2,12)
    assert round(turtle._right[2],12) == 0
    # TODO: Figure out exact math.  SymPy maybe?

def test_right():
    turtle = machine.turtle()
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.right(90)
    assert turtle._heading  == [0,-1,0] # Looking down the -Y axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [-1,0,0] # Looking down the -X axis
    assert turtle.pos()     == [0,0,0]
    turtle.right(-90)
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.right(0)
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.right(90+360)
    assert turtle._heading  == [0,-1,0] # Looking down the -Y axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [-1,0,0] # Looking down the -X axis
    assert turtle.pos()     == [0,0,0]
    turtle.right(-90-360)
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]

def test_rt():
    turtle = machine.turtle()
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.rt(90)
    assert turtle._heading  == [0,-1,0] # Looking down the -Y axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [-1,0,0] # Looking down the -X axis
    assert turtle.pos()     == [0,0,0]
    turtle.rt(-90)
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.rt(0)
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.rt(90+360)
    assert turtle._heading  == [0,-1,0] # Looking down the -Y axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [-1,0,0] # Looking down the -X axis
    assert turtle.pos()     == [0,0,0]
    turtle.rt(-90-360)
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]

def test_left():
    turtle = machine.turtle()
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.left(90)
    assert turtle._heading  == [0,1,0]  # Looking down the +Y axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [1,0,0]  # Looking down the +X axis
    assert turtle.pos()     == [0,0,0]
    turtle.left(-90)
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.left(0)
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.left(90+360)
    assert turtle._heading  == [0,1,0]  # Looking down the +Y axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [1,0,0]  # Looking down the +X axis
    assert turtle.pos()     == [0,0,0]
    turtle.left(-90-360)
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]

def test_lt():
    turtle = machine.turtle()
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.lt(90)
    assert turtle._heading  == [0,1,0]  # Looking down the +Y axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [1,0,0]  # Looking down the +X axis
    assert turtle.pos()     == [0,0,0]
    turtle.lt(-90)
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.lt(0)
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]
    turtle.lt(90+360)
    assert turtle._heading  == [0,1,0]  # Looking down the +Y axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [1,0,0]  # Looking down the +X axis
    assert turtle.pos()     == [0,0,0]
    turtle.lt(-90-360)
    assert turtle._heading  == [1,0,0]  # Looking down the +X axis
    assert turtle._normal   == [0,0,1]  # Normal should always be +Z in 2D
    assert turtle._right    == [0,-1,0] # Looking down the -Y axis
    assert turtle.pos()     == [0,0,0]

def test_home_pen_up():
    turtle = machine.turtle()
    turtle._machine.feed = 500
    turtle.forward(10)
    turtle.right(15)
    turtle.forward(10)
    assert turtle.pos()     != [0,0,0]
    assert turtle._heading  != [1,0,0]
    turtle.home()
    assert turtle.pos()     == [0,0,10]
    assert turtle._heading  == [1,0,0]

def test_home_pen_down():
    turtle = machine.turtle()
    turtle._machine.feed = 500
    turtle.pendown()
    turtle.forward(10)
    turtle.right(15)
    turtle.forward(10)
    assert turtle.pos()     != [0,0,0]
    assert turtle._heading  != [1,0,0]
    turtle.home()
    assert turtle.pos()     == [0,0,0]
    assert turtle._heading  == [1,0,0]

def test_circle_ccw():
    turtle = machine.turtle()
    turtle.circle(1,180)
    assert round(turtle.pos()[0],12) == 0
    assert round(turtle.pos()[1],12) == 2
    assert round(turtle.pos()[0],12) == 0
    assert round(turtle._heading[0],12) == -1
    assert round(turtle._heading[1],12) == 0
    assert round(turtle._heading[2],12) == 0
    # TODO: Figure out exact math.  SymPy maybe?

def test_circle_cw():
    turtle = machine.turtle()
    turtle.circle(-1,180)
    assert round(turtle.pos()[0],12) == 0
    assert round(turtle.pos()[1],12) == -2
    assert round(turtle.pos()[0],12) == 0
    assert round(turtle._heading[0],12) == -1
    assert round(turtle._heading[1],12) == 0
    assert round(turtle._heading[2],12) == 0
    # TODO: Figure out exact math.  SymPy maybe?

def test_smooth_circle_cw():
    turtle = machine.turtle()
    turtle.circle(-1,180,10000)
    assert round(turtle.pos()[0],12) == 0
    assert round(turtle.pos()[1],12) == -2
    assert round(turtle.pos()[0],12) == 0
    assert round(turtle._heading[0],12) == -1
    assert round(turtle._heading[1],12) == 0
    assert round(turtle._heading[2],12) == 0
    # TODO: Figure out exact math.  SymPy maybe?
