from cell import *
import random, math

class Grid :
    def __init__(self, size, obstacles = 0.7, traps = 0.1, rest = 0.03) :
        self.entries = [[None for i in range(size)] for j in range(size)]
        self.size = size
        self.path = [] # Guaranteed path from S to E
        self.cells = [] # Guaranteed path from portals to path
        self.obstacle_number = obstacles # Percentage of obstacles in remaining cells
        self.traps = traps
        self.rest = rest

        self.start = (0, 0)
        self.end = (size - 1, size - 1)
        self.portal_top = (size - 1, 0)
        self.portal_bottom = (0, size - 1)

        # Creates a guaranteed path from S to E
        self.create_path(self.end, self.start, self.path)

        # Targets closest point to portal
        top_target = self.get_target(self.portal_top)
        bottom_target = self.get_target(self.portal_bottom)

        # Creates a guaranteed path from portals to path
        self.create_path(top_target, self.portal_top, self.cells)
        self.create_path(self.portal_bottom, bottom_target, self.cells)


        self.corners = [(0, 0), (size - 1, size - 1), self.portal_bottom, self.portal_top]

        # Fill the rest with obstacles and switches
        self.random_rest()
        
        self[0, 0] = Start()
        self[size - 1, size - 1] = End()
        self[self.portal_top] = Portal(self.portal_bottom)
        self[self.portal_bottom] = Portal(self.portal_top)
        
        self.paths = self.path + self.cells
        # Finds accessible cells from each cell
        self.adjacency()

    def __getitem__(self, coordinates) :
        if isinstance(coordinates, tuple) :
            return self.entries[coordinates[1]][coordinates[0]]
        else :
            return self.entries[coordinates]
    
    def __setitem__(self, coordinates, x) :
        if isinstance(coordinates, tuple) :
            self.entries[coordinates[1]][coordinates[0]] = x
        else :
            self.entries[coordinates] = x

    def __repr__(self) :
        corner = "\\"
        result = f"{corner:^5}" + "".join([f"{num:^5}" for num in range(self.size)]) + "\n"
        i = 0
        for row in self.entries :
            result += f"{i:^5}"
            for cell in row :
                result += f"{str(cell):^5}"
            result += "\n"
            i += 1
        return result
    
    def create_path(self, start, end, path) :
        reverseX = start[0] <= end[0]
        reverseY = start[1] <= end[1]
        deltaX = 1 if reverseX else -1
        deltaY = 1 if reverseY else -1

        if type(start) != tuple or type(end) != tuple :
            raise TypeError("Coordinates must be integer tuples")
        x, y = start
        while (x, y) != end :
            if x == end[0] :
                while y != end[1] :
                    path.append((x, y))
                    self[x, y] = Cell()
                    y += deltaY
                return
            elif y == end[1] :
                while x != end[0] :
                    path.append((x, y))
                    self[x, y] = Cell()
                    x += deltaX
                return
            else :
                path.append((x, y))
                self[x, y] = Cell()
                if random.randint(1, 2) == 1 :
                    x += deltaX
                else :
                    y += deltaY
    
    def random_rest(self) :
        for i in range(self.size) :
            for j in range(self.size) :
                x = random.random()
                self[i, j] = Cell()
                if any([(i, j) in li for li in [self.corners, self.path, self.cells]]) :
                    if x < self.traps :
                        self[i, j] = Trap()
                    elif x < self.traps + self.rest :
                        self[i, j] = RestArea()
                    continue
                if x < self.traps + self.rest + self.obstacle_number :
                    self[i, j] = Obstacle()
                

    def get_other_portal(self, key) :
        return (0, self.size - 1) if key == (self.size - 1, 0) else (self.size - 1, 0) 

    def get_target(self, portal) :
        distances = [self.distance(portal, point) for point in self.path]
        return self.path[distances.index(min(distances))]
    
    def distance(self, cell1, cell2) :
        return math.sqrt(int(abs(cell1[0] - cell2[0]) ** 2 + abs(cell1[1] - cell2[1]) ** 2))
    
    def adjacency(self) :
        for i in range(self.size) :
            for j in range(self.size) :
                adjacent = []
                if i != 0 and not type(self[i - 1, j]) == Obstacle:
                    self[i, j].neighbors["left"] = (i - 1, j)
                if j != 0 and not type(self[i, j - 1]) == Obstacle :
                    self[i, j].neighbors["up"] = (i, j - 1)
                if i != self.size - 1 and not type(self[i + 1, j]) == Obstacle :
                    self[i, j].neighbors["right"] = (i + 1, j)
                if j != self.size - 1 and not type(self[i, j + 1]) == Obstacle :
                    self[i, j].neighbors["down"] = (i, j + 1)
        
        for i in range(self.size) :
            for j in range(self.size) :
                if len(self[i, j].neighbors) == 0 :
                    self[i, j] = Obstacle()
    
    def reward_map(self) :
        result = "".join([f"{num:^5}" for num in range(-1, self.size)]) + "\n"
        i = 0
        for row in self.entries :
            result += f"{i:^5}"
            for cell in row :
                result += f"{cell.get_reward():^5}"
            result += "\n"
            i += 1
        return result

