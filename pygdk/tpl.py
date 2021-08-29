################################################################################
# Tool Path Language
# https://tplang.org/
################################################################################

################################################################################
# Tool Movement
# https://tplang.org/#motion
################################################################################

def rapid(x=None, y=None, z=None, a=None, b=None, c=None, u=None, v=None, w=None, incremental=False):
    print("Rapid:", x, y, z, a, b, c, u, v, w, incremental)

def irapid(x=None, y=None, z=None, a=None, b=None, c=None, u=None, v=None, w=None, incremental=True):
    rapid(x,y,z,a,b,c,u,v,w,incremental)

def cut(x=None, y=None, z=None, a=None, b=None, c=None, u=None, v=None, w=None, incremental=False):
    print("Cut:", x, y, z, a, b, c, u, v, w, incremental)

def icut(x=None, y=None, z=None, a=None, b=None, c=None, u=None, v=None, w=None, incremental=True):
    cut(x,y,z,a,b,c,u,v,w,incremental)

def arc(x=None, y=None, z=None, angle=None, plane=None):
    print("Arc:", x, y, z, angle, plane)

def probe(x=None, y=None, z=None, a=None, b=None, c=None, u=None, v=None, w=None, port=0, active=True, error=True):
    print("Probe:", x, y, z, a, b, c, u, v, w, port, active, error)

def dwell(seconds=None):
    print("Dwell:", seconds)

################################################################################
# Machine State
# https://tplang.org/#mstate
################################################################################

FEED_UNITS_PER_MIN = 0
FEED_INVERSE_TIME  = 1
FEED_UNITS_PER_REV = 2

def feed(rate=None, mode=FEED_UNITS_PER_MIN):
    print("Feed:", rate, mode)

def speed(rate=None, surface=None, max=None):
    print("Speed:", rate, surface, max)

CYLINDRICAL = 0
CONICAL     = 1
BALLNOSE    = 2
SPHEROID    = 3
SNUBNOSE    = 4

def tool(number=None):
    print("Tool:", number)

METRIC   = 0
IMPERIAL = 1

def units(type=None):
    print("Units:", type)

def pause(optional=False):
    print("Pause:", optional)

def workpiece():
    print("Workpiece:")
