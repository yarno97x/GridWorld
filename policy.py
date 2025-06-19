import numpy as np, copy 
from cell import *
from grid import Grid
import matplotlib.pyplot as plt

from enum import Enum

class Direction(Enum) :
    RIGHT = '→' 
    UP = '↑' 
    DOWN = '↓'
    LEFT = '←'

class PolicyAlgorithm :
    def __init__(self, grid, synchronous = False, epochs = 1000, tolerance = 0.01) :
        self.grid = grid
        # print(self.grid)
        self.epochs = epochs
        self.tolerance = tolerance
        self.policy = self.create_empty_policy(zeros = False)
        self.value_function = self.create_empty_value_function()
        self.value_function[self.grid.end] = 0
        # print(self.value_function)
        self.synchronous = synchronous

    def create_empty_policy(self, zeros = False) :
        new_policy = {}
        for i in range(self.grid.size) :
            for j in range(self.grid.size) :
                if any([isinstance(self.grid[i, j], x) for x in [End, Obstacle]]) :
                    continue
                neighbors = self.grid[(i, j)].neighbors.values()
                probability = 0 if zeros else 1 / len(self.grid[(i, j)].neighbors)
                new_policy[(i, j)] = {neighbor : probability for neighbor in neighbors}
        return new_policy

    def create_empty_value_function(self) :
        new_function = {}
        for i in range(self.grid.size) :
            for j in range(self.grid.size) :
                if any([isinstance(self.grid[i, j], x) for x in [End, Obstacle]]) :
                    continue
                new_function[(i, j)] = 0
        return new_function

    def policy_convergence(self, old_policy) :
        return self.policy == old_policy
    
    def value_function_convergence(self, old_value_function) :
        if len(old_value_function) != len(self.value_function) :
            raise ValueError("Value functions do not have the same size")
        
        total = 0
        for key, value in self.value_function.items() :
            total += abs(value - old_value_function[key]) ** 2
        return total 
    
    def repr_value_function(self) :
        corner = "\\"
        result = f"{corner:^6}" + "".join([f"{num:^6}" for num in range(self.grid.size)]) + "\n"
        k = 0
        for j in range(self.grid.size) :
            result += f"{k:^6}"
            for i in range(self.grid.size) :
                if (i, j) in self.value_function.keys() :
                    key = (i, j)
                    if self.value_function[(i, j)] < -1 * self.grid.size ** 2 :
                        x = f"X"
                        result += f"{x:^6}"
                        continue
                    result += f"{self.value_function[key]:^6}"
                else :
                    x = f"X"
                    result += f"{x:^6}"
            result += "\n"
            k += 1
        return result
    
    def find_direction(self, key) :
        policy = self.policy[key]
        i, j = key
        y, x = 0, 0
        for coord in policy.keys() :
            if policy[coord] == 1 :
                x, y = coord
                break
        if x - i > 0 :
            return Direction.RIGHT.value
        elif x - i < 0 :
            return Direction.LEFT.value
        elif y - j > 0 :
            return Direction.DOWN.value
        else :
            return Direction.UP.value

    def repr_policy(self) :
        corner = "\\"
        result = f"{corner:^6}" + "".join([f"{num:^6}" for num in range(self.grid.size)]) + "\n"
        k = 0
        for j in range(self.grid.size) :
            result += f"{k:^6}"
            for i in range(self.grid.size) :
                if (i, j) in self.value_function.keys() :
                    if (i, j) == self.grid.end :
                        result += f"{'E':^6}"
                        continue
                    key = (i, j)
                    if self.value_function[(i, j)] < -1 * self.grid.size ** 2 :
                        x = f"X"
                        result += f"{x:^6}"
                        continue
                    symbol = self.find_direction(key)
                    if isinstance(self.grid[i, j], Trap) :
                        symbol += "*"
                    result += f"{f'{symbol}':^6}"
                else :
                    x = f"X"
                    result += f"{x:^6}"
            result += "\n"
            k += 1
        return result

    def derive_policy(self) :
        diffs = []
        for i in range(self.epochs) :
            # print(i)
            old_policy = copy.deepcopy(self.policy)
            old_value_function = copy.deepcopy(self.value_function)

            self.process()
            # print(self.repr_value_function())
            
            x = True
            if isinstance(self, PolicyIteration) :
                x = self.policy_convergence(old_policy)

            diff = self.value_function_convergence(old_value_function)
            diffs.append(diff)

            if x and diff < self.tolerance:
                if isinstance(self, ValueIteration) :
                    self.policy_improvement()
                return np.array(diffs) 
        if isinstance(self, ValueIteration) :
            self.policy_improvement()
        return np.array(diffs)

    def convergence_analysis(self) :
        diffs = self.derive_policy()
        x = np.arange(len(diffs))
        plt.scatter(x, diffs)
        plt.show()

    def value_fct(self) :
        VF = []
        for j in range(self.grid.size) :
            row = []
            for i in range(self.grid.size) :
                if (i, j) in self.value_function.keys() :
                    key = (i, j)
                    if self.value_function[(i, j)] < -1 * self.grid.size ** 2 :
                        row.append("X")
                        continue
                    row.append(f"{self.value_function[key]}") 
                else :
                    row.append("X")
            VF.append(row)
        return VF

    def arrow_grid(self):
        result = []
        for j in range(self.grid.size):
            row = []
            for i in range(self.grid.size):
                key = (i, j)

                if key not in self.value_function:
                    row.append("X")
                    continue

                if key == self.grid.end:
                    row.append("E")
                    continue

                if self.value_function[(i, j)] < -1 * self.grid.size ** 2:
                    row.append("X")
                    continue

                symbol = self.find_direction(key)

                row.append(symbol)
            result.append(row)
        return result
    
    def policy_improvement(self) :
        # print("IMPROVING")
        new_policy = self.create_empty_policy(zeros = True)
        for base in self.value_function :
            if base == self.grid.end :
                continue
            maximum = None
            max_coord = None
            # print(self.policy[base])
            for neighbor in self.policy[base].keys() :
                if not maximum :
                    maximum = self.value_function[neighbor]
                    max_coord = neighbor
                    new_policy[base][neighbor] = 1
                elif maximum < self.value_function[neighbor] :
                    new_policy[base][max_coord] = 0
                    new_policy[base][neighbor] = 1
                    maximum = self.value_function[neighbor]
                    max_coord = neighbor
        self.policy = new_policy  

class PolicyIteration(PolicyAlgorithm) :
    def __init__(self, grid, synchronous = True) -> None :
        super().__init__(grid, synchronous)

    def process(self) :
        # print("EVALUATING")
        if self.synchronous :
            self.value_function = self.policy_eval_sync()
        else :
            self.policy_eval_async()

        # print(self.value_function)
        # print(self.repr_value_function())

        self.policy_improvement()
        #print(self.repr_policy())

    def policy_eval_sync(self) :
        new_function = self.create_empty_value_function()
        # print(new_function)
        for base in self.value_function :
            # print(f"Base {base}")
            if base == self.grid.end :
                continue
            # print(self.policy[base])

            value = self.grid[base].get_reward()
            for neighbor in self.policy[base].keys() :
                # print(self.policy[base][neighbor])
                value += self.policy[base][neighbor] * self.value_function[neighbor]
            new_function[base] = value
            new_function[self.grid.end] = 0
            new_function[self.grid.size - 1, 0], new_function[0, self.grid.size - 1] = new_function[0, self.grid.size - 1], new_function[self.grid.size - 1, 0] 
        # print(new_function)
        return new_function

    def policy_eval_async(self) :
        # print(self.policy)
        for base in self.value_function :
            # print(f"Base {base}")
            if base == self.grid.end :
                continue
            # print(f"{self.policy[base]} -?")

            value = self.grid[base].get_reward()
            for neighbor in self.policy[base].keys() :
                # print(self.value_function[neighbor])
                # print(self.policy[base][neighbor])
                value += self.policy[base][neighbor] * self.value_function[neighbor]
            self.value_function[base] = value
        self.value_function[self.grid.end] = 0
        self.value_function[self.grid.size - 1, 0], self.value_function[0, self.grid.size - 1] = self.value_function[0, self.grid.size - 1], self.value_function[self.grid.size - 1, 0]         

class ValueIteration(PolicyAlgorithm) :
    def __init__(self, grid, synchronous = False) -> None :
        super().__init__(grid, synchronous)
        # print(grid.size)

    def value_iter_sync(self) :
        new_value_function = self.create_empty_value_function()
        for base in self.value_function :
            coords = self.grid[base].neighbors.values()
            values = [self.grid[base].get_reward() + self.value_function[coord] for coord in coords]
            new_value_function[base] = round(max(values), 3)
        new_value_function[(self.grid.end)] = 0
        return new_value_function
    
    def value_iter_async(self) :
        for base in self.value_function :
            coords = self.grid[base].neighbors.values()
            values = [self.grid[base].get_reward() + self.value_function[coord] for coord in coords]
            self.value_function[base] = round(max(values), 3)
        self.value_function[self.grid.end] = 0

    def process(self) :
        if self.synchronous :
            self.value_function = self.value_iter_sync()
        else :
            self.value_iter_async()        

if __name__ == "__main__" :
    g = Grid(5)
    p = PolicyIteration(g, False)
    q = PolicyIteration(g, True)
    r = ValueIteration(g, False)
    s = ValueIteration(g, True)
    p.derive_policy()
    q.derive_policy()
    r.derive_policy()
    s.derive_policy()
    print(p.repr_policy())
    print(q.repr_policy())
    print(r.repr_policy())
    print(s.repr_policy())
            
