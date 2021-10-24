import json

from .machine import Machine

RED    = '\033[31m'
ORANGE = '\033[91m'
YELLOW = '\033[93m'
GREEN  = '\033[92m'
CYAN   = '\033[36m'
ENDC   = '\033[0m'

################################################################################
# Initializer -- Load details from JSON
################################################################################

class Plotter(Machine):
    def __init__(self, json_file, safe_z=10):
        super().__init__(json_file)
        self.queue(comment='Loading Plotter parameters from JSON', style='plotter')
        with open(f"machines/{json_file}") as f:
            if 'Plotter' not in self.dict:
                raise KeyError(f"Machine config does not include Plotter.  See https://github.com/cilynx/pygdk/blob/main/onefinity.json for an example Plotter config.")
            self._plotter = self.dict['Plotter']
            if 'Tool Table' not in self.dict:
                raise KeyError(f"{RED}You machine configuration must reference a tool table file{ENDC}")
            with open(f"tables/{self.dict['Tool Table']}", 'r') as tt:
                self._tool_table = json.load(tt)

        self.safe_z = safe_z

################################################################################
# Pen Color
################################################################################

    @property
    def pen_color(self):
        return self.tool._description

    @pen_color.setter
    def pen_color(self, value):
        if not self._plotter:
            raise ValueError(f"{RED}You must configure a Plotter before you can set pen_color{ENDC}")

        if self._optimize:
            if value is None:
                self.optimize_linear_moves()
            elif any(value in row for row in self._plotter['Magazine']):
                self._linear_moves.setdefault(value,[])
                self._optimize_tool = value
            else:
                raise ValueError(f"{RED}'{value}' is not a configured color.  Options are: {self._plotter['Magazine']}" )

        else:
            self.rapid(z=self._plotter['Z-Stage'], comment="Go to pen change staging height")
            if self.tool:
                self.rapid(x=self._plotter['Slot Zero'][0], y=self._plotter['Slot Zero'][1], z=self._plotter['Z-Stage'], comment="Stage to retract current pen")
                self.rapid(z=self._plotter['Z-Click'], comment="Retract current pen")
                self.rapid(z=self._plotter['Z-Stage'], comment="Return to pen change stage")
            if value is None:
                self.x_offset = 0;
                self.y_offset = 0;
                rows = len(self._plotter['Magazine'])
                backset = self._plotter['Slot Zero'][1] + (rows+1)*self._plotter['Pen Spacing'];
                self.rapid(x=self._plotter['Slot Zero'][0], y=backset, comment="Rapid to homing-safe backset")
                return self.tool
            for row in self._plotter['Magazine']:
                if value in row:
                    i = row.index(value)
                    j = self._plotter['Magazine'].index(row)
                    self.x_offset = -i*self._plotter['Pen Spacing']
                    self.y_offset = j*self._plotter['Pen Spacing']
                    self.rapid(x=self._plotter['Slot Zero'][0], y=self._plotter['Slot Zero'][1], z=self._plotter['Z-Stage'], comment="Stage to activate new pen")
                    self.rapid(z=self._plotter['Z-Click'], comment="Activate new pen")
                    self.rapid(z=self._plotter['Z-Stage'], comment="Return to pen change stage")
                    self.tool = value
                    return self.tool
            raise ValueError(f"{RED}'{value}' is not a configured color.  Options are: {self._plotter['Magazine']}" )

################################################################################
# Optimize Linear Moves
################################################################################


    def optimize_linear_moves(self):
        self._optimize = False
        turtle = self.turtle(verbose=True, z_draw=-124)
        for color in self._linear_moves:
            if color:
                self.pen_color = color
                pos = self._plotter['Slot Zero']
                remaining_points = self._linear_moves[color]
                while remaining_points:
                    shortest = None
                    winner = None
                    for pair in remaining_points:
                        for point in pair:
                            ds = dsq(pos, point)
                            if shortest is None or ds < shortest:
                                shortest = ds
                                winner = pair
                    remaining_points.remove(winner)
                    points = order(winner, pos)
                    turtle.penup()
                    turtle.goto(points[0][0], points[0][1], comment="Rapid to next start")
                    turtle.pendown()
                    turtle.goto(points[1][0], points[1][1], comment="Draw next line")
                    pos = points[1]
                    # self.rapid(move[0][0], move[0][1], move[0][2], comment="Rapid to next start")
                    # self.linear_interpolation(move[1][0], move[1][1], move[1][2], comment="Execute move")

def dsq(a, b):
    return (b[0]-a[0])**2 + (b[1]-a[1])**2

def order(pair, pos):
#    print(pair if dsq(pos, pair[0]) < dsq(pos, pair[1]) else [pair[1], pair[0]])
    return pair if dsq(pos, pair[0]) < dsq(pos, pair[1]) else [pair[1], pair[0]]
