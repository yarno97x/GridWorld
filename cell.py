import random
class Cell :
    def __init__(self, reward = -1) :
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
        super().__init__("X")

class Portal(Cell) :
    def __init__(self, towards):
        if type(towards) != tuple :
            raise TypeError("Portal needs endpoint tuple")
        super().__init__()
        self.towards = towards

class Trap(Cell) :
    def __init__(self) :
        super().__init__(-10)

class Start(Cell) :
    def __init__(self):
        super().__init__(-1)

class End(Cell) :
    def __init__(self):
        super().__init__(0)
