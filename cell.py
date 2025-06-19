import random

class Cell :
    def __init__(self, reward_mean = -1, reward_std = 1, deterministic = True) :
        self.reward_mean = reward_mean
        self.reward_std = reward_std 
        self.neighbors = {}
        self.deterministic = deterministic
    
    def get_reward(self) :
        if self.deterministic :
            return self.reward_mean
        return random.gauss(self.reward_mean, self.reward_std)
    
    def __repr__(self) :
        if type(self) == Cell :
            return "[ ]"
        elif type(self) == Obstacle :
            return "[X]"
        elif type(self) == Portal :
            return "[O]"
        elif type(self) == Start :
            return "[S]"
        elif type(self) == End :
            return "[E]"
        else :
            return "[*]"

class Obstacle(Cell) :
    def __init__(self) :
        super().__init__("X")

class Portal(Cell) :
    def __init__(self, towards):
        if type(towards) != tuple :
            raise TypeError("Portal needs endpoint tuple")
        super().__init__()
        self.towards = towards

class Trap(Cell) :
    def __init__(self) :
        super().__init__(-10, 2)

class Start(Cell) :
    def __init__(self):
        super().__init__(-5)

class End(Cell) :
    def __init__(self):
        super().__init__(100)

class RestArea(Cell) :
    def __init__(self):
        super().__init__(0)