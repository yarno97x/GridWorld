from grid import Grid
import copy
from cell import Obstacle, End

class Model :
    def __init__(self, grid, deterministic, epsilon = 0.2):
        """Constructs either a deterministic or stochastic model of the environment

        Args:
            grid (Grid): The grid of states
            deterministic (boolean): Whether the model is stochastic or deterministic
            epsilon (float, optional): The probability of misfiring. Defaults to 0.3.
        """
        self.grid = grid
        self.deterministic = deterministic
        self.epsilon = epsilon
        self.states = [(i, j) for i in range(self.grid.size) for j in range(self.grid.size)]
        self.state_action_pairs = {state : [action for action in self.grid[state].neighbors.values()] for state in self.states}
        self.transitions = {}
        if self.deterministic :
            self.transitions = {(state, action) : {action : 1} for state in self.states for action in self.grid[state].neighbors.values()} 
        else :
            for state in self.states :
                if any([isinstance(self.grid[state], x) for x in [Obstacle, End]]) :
                    continue
                for action in self.state_action_pairs[state] :
                    others = copy.deepcopy(self.state_action_pairs[state])
                    others.pop(others.index(action))
                    if len(others) == 0 : 
                        self.transitions[(state, action)] = {action : 1}
                    else :
                        self.transitions[(state, action)] = {action : 1 - self.epsilon} | {other : self.epsilon / len(others) for other in others}

    def conditional_probability(self, s, a, true_action) :
        return self.transitions[(s, a)][true_action]   
    
    def __repr__(self) :
        result = ""
        for trans in self.transitions.items() :
            result += f"{trans}\n"
        return result



if __name__ == "__main__" :
    g = Grid(4)
    m = Model(g, False, 0.2)
    print(m)
    print(g)
