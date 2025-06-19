from grid import Grid
class Model :
    def __init__(self, grid, deterministic, epsilon = 0):
        self.grid = grid
        self.deterministic = deterministic
        if self.deterministic :
            states = [(i, j) for i in range(self.grid.size) for j in range(self.grid.size)]

            self.transitions = {(state, action) : {action : 1} for state in states for action in self.grid[state].neighbors.keys()} 

g = Grid(5)
m = Model(g, True)
print(m.transitions)