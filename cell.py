import random
class Cell :
    def __init__(self, reward = -1) :
        if type(reward) not in [int, float] :
            raise TypeError("Reward must be a numerical value")
        self.reward = reward
        self.neighbors = {}
    
    def get_reward(self) :
        return self.reward
    
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
        super().__init__()

class Portal(Cell) :
    def __init__(self, towards):
        if type(towards) != tuple :
            raise TypeError("Portal needs endpoint tuple")
        super().__init__(0)
        self.towards = towards

class Trap(Cell) :
    def __init__(self) :
        super().__init__(random.randint(-100, -10))

class Start(Cell) :
    def __init__(self):
        super().__init__(0)

class End(Cell) :
    def __init__(self):
        super().__init__(0)
