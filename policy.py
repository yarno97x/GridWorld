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
    def __init__(self, grid, epochs = 1000, tolerance = 0.01) :
        self.grid = grid
        self.epochs = epochs
        self.tolerance = tolerance
        self.policy = self.create_empty_policy(zeros = False)
        self.value_function = self.create_empty_value_function()
        self.value_function[self.grid.end] = 0

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
        print("HELLO")
        for i in range(self.epochs) :
            print(i)
            old_policy = copy.deepcopy(self.policy)
            old_value_function = copy.deepcopy(self.value_function)

            self.process()
            
            diff = self.value_function_convergence(old_value_function)
            diffs.append(diff)
            if self.policy_convergence(old_policy) and diff < self.tolerance:
                print(self.repr_policy())
                return np.array(diffs) 
        print(self.repr_policy())
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
                if isinstance(self.grid[i, j], Trap):
                    symbol += "*"

                row.append(symbol)
            result.append(row)
        return result

class PolicyIteration(PolicyAlgorithm) :
    def __init__(self, grid, synchronous = True) -> None :
        super().__init__(grid)
        self.synchronous = synchronous

    def process(self) :
        # print("EVALUATING")
        if self.synchronous :
            self.value_function = self.policy_eval_sync()
        else :
            self.policy_eval_async()

        # print(self.value_function)
        # print(self.repr_value_function())

        self.policy = self.policy_improvement()
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
            self.new_function[self.grid.size - 1, 0], self.new_function[0, self.grid.size - 1] = self.new_function[0, self.grid.size - 1], self.new_function[self.grid.size - 1, 0] 
        # print(new_function)
        return new_function

    def policy_eval_async(self) :
        for base in self.value_function :
            # print(f"Base {base}")
            if base == self.grid.end :
                continue
            # print(self.policy[base])

            value = self.grid[base].get_reward()
            for neighbor in self.policy[base].keys() :
                # print(self.value_function[neighbor])
                # print(self.policy[base][neighbor])
                value += self.policy[base][neighbor] * self.value_function[neighbor]
            self.value_function[base] = value
        self.value_function[self.grid.end] = 0
        self.value_function[self.grid.size - 1, 0], self.value_function[0, self.grid.size - 1] = self.value_function[0, self.grid.size - 1], self.value_function[self.grid.size - 1, 0] 

    def policy_improvement(self) :
        # print("IMPROVING")
        new_policy = self.create_empty_policy(zeros = True)
        for base in self.policy :
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
        return new_policy          

class ValueIteration(PolicyAlgorithm) :
    def __init__(self, grid) -> None :
        super().__init__(grid)

    def process(self) :
        pass
