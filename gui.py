import tkinter as tk
from grid import Grid
from policy import *
from cell import *

class Visualizer(tk.Tk) :
    def __init__(self):
        super().__init__()
        self.title("GridWorld GUI")

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.n = 3
        self.obstacles = 0.5
        self.rest = 0.05
        self.traps = 0.1
        self.generate_grid()
        self.frames = {}

        for F in (Menu, UnsolvedGrid, ArrowGradient, ValueFunction):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Menu)    
    
    def show_frame(self, page_class):

        if page_class not in self.frames:
            frame = page_class(self.container, self)
            self.frames[page_class] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        frame = self.frames[page_class]
        frame.tkraise()

        # Redraw grid on frames that have draw_grid method
        if hasattr(self, "p") and hasattr(frame, "draw_grid"):
            frame.draw_grid()


    def generate_grid(self) :
        self.grid = Grid(self.n, self.obstacles, self.traps, self.rest)

    def find_policy(self, PI) :
        if PI :
            print("PI")
            self.p = PolicyIteration(self.grid, False)
        else :
            self.p = ValueIteration(self.grid)
        self.p.derive_policy()

    def get_color(self, cell) :
        if isinstance(cell, Obstacle) :
            return "black"
        elif isinstance(cell, Portal) :
            return "blue"
        elif isinstance(cell, Trap) :
            return "red"
        elif isinstance(cell, Start) :
            return "yellow"
        elif isinstance(cell, End) :
            return "green"
        elif isinstance(cell, RestArea) :
            return "pink"
        else :
            return "white" 

class Menu(tk.Frame) :
    def __init__(self, parent, controller) :
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="Main Menu").pack(pady=10)
        tk.Button(self, text="Generate a grid", command= lambda : self.generate()).pack()

        tk.Label(self, text="Grid size:").pack()
        self.size_spinbox = tk.Spinbox(self, from_=3, to=20, textvariable=tk.StringVar(value="15"))  
        self.size_spinbox.pack()

        tk.Label(self, text="Obstacles:").pack()
        self.obs_spinbox = tk.Spinbox(self, from_=0, to=100, textvariable=tk.StringVar(value="50"))  
        self.obs_spinbox.pack()

        tk.Label(self, text="Traps:").pack()
        self.trap_spinbox = tk.Spinbox(self, from_=0, to=100, textvariable=tk.StringVar(value="10"))  
        self.trap_spinbox.pack()
        
        tk.Label(self, text="Rest areas:").pack()
        self.rest_spinbox = tk.Spinbox(self, from_=0, to=100, textvariable=tk.StringVar(value="2"))  
        self.rest_spinbox.pack()

    def generate(self):
        size = self.size_spinbox.get()  
        obs = int(self.obs_spinbox.get()) / 100
        traps = int(self.size_spinbox.get()) / 100 
        rest = int(self.rest_spinbox.get()) / 100
        # print(obs)
        # print(traps)
        # print(rest)
        # print(f"% is {traps + obs + rest}")
        if traps + obs + rest > 1 :
            raise ValueError("Please enter a valid integer.")
        try:
            self.controller.n = int(size)
            self.controller.obstacles = obs
            self.controller.traps = traps
            self.controller.rest = rest

            self.controller.generate_grid()
            print(self.controller.grid)
            self.draw_grid()
            self.controller.show_frame(UnsolvedGrid)
        except ValueError:
            print("Please enter a valid integer.")
    
    def draw_grid(self) :  
        self.controller.frames[UnsolvedGrid].draw_grid()



class UnsolvedGrid(tk.Frame) :
    def __init__(self, parent, controller) :
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Unsolved Grid").pack(pady=10)
        tk.Button(self, text="Back to Menu",
                  command=lambda: controller.show_frame(Menu)).pack()
        tk.Button(self, text="Regenerate",
                  command=self.regen).pack()
        tk.Button(self, text="Compute Policy Iteration", command=lambda : self.controller.find_policy(True)).pack()
        tk.Button(self, text="Compute Value Iteration", command=lambda :self.controller.find_policy(False)).pack()

        tk.Button(self, text="Compute Arrow Gradient", command=lambda: self.show_values(ArrowGradient)).pack()
        tk.Button(self, text="Compute Value Function", command=lambda: self.show_values(ValueFunction)).pack()

        self.width = 800
        self.canvas = tk.Canvas(self, width=self.width, height=self.width)
        self.draw_grid()
        self.canvas.pack(padx=50)

    def show_values(self, frameType) :
        if hasattr(self.controller, "p") and self.controller.p :
            self.controller.show_frame(frameType)

    def regen(self) :
        self.canvas.delete("all")
        self.controller.generate_grid()
        self.controller.p = None
        self.draw_grid()
        self.controller.show_frame(UnsolvedGrid)

    def draw_grid(self):
        self.canvas.delete("all")
        g = self.controller.grid
        cell_size = self.width / (g.size * 1.8)
        for i in range(g.size):
            for j in range(g.size):
                cell = g[j, i]
                color = self.controller.get_color(cell)
                self.canvas.create_rectangle(j*cell_size, i*cell_size,
                                             (j+1)*cell_size, (i+1)*cell_size,
                                             fill=color, outline="gray")

class ArrowGradient(tk.Frame) :
    def __init__(self, parent, controller) :
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="Arrow Gradient").pack(pady=10)
        tk.Button(self, text="Back to Menu",
                  command=lambda: controller.show_frame(Menu)).pack()
        tk.Button(self, text="Value Function",
                  command=lambda: controller.show_frame(ValueFunction)).pack()
    
        self.width = 800
        self.canvas = tk.Canvas(self, width=self.width, height=self.width)
        self.canvas.pack(padx=50)
    
    def draw_grid(self):    
        if not hasattr(self.controller, "p") or self.controller.p is None:
            print("Policy not yet computed.")
            return
        self.canvas.delete("all")
        g = self.controller.grid
        cell_size = self.width / (g.size * 1.8)
        for i in range(g.size):
            for j in range(g.size):
                cell = g[i, j]
                color = self.controller.get_color(cell)
                x0 = i * cell_size
                y0 = j * cell_size
                x1 = (i + 1) * cell_size
                y1 = (j + 1) * cell_size

                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="gray")

                text_x = (x0 + x1) / 2
                text_y = (y0 + y1) / 2

                x = self.controller.p.arrow_grid()[j][i]
                self.canvas.create_text(text_x, text_y, text=f"{x}", fill="black")

class ValueFunction(tk.Frame) :
    def __init__(self, parent, controller) :
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="Value Function").pack(pady=10)
        tk.Button(self, text="Back to Menu",
                  command=lambda: controller.show_frame(Menu)).pack()
        tk.Button(self, text="Arrow Gradient",
                  command=lambda: controller.show_frame(ArrowGradient)).pack()
        
        self.width = 800
        self.canvas = tk.Canvas(self, width=self.width, height=self.width)
        self.canvas.pack(padx=50)
    
    def draw_grid(self):
        if not hasattr(self.controller, "p") or self.controller.p is None:
            print("Policy not yet computed.")
            return
        self.canvas.delete("all")
        g = self.controller.grid
        cell_size = self.width / (g.size * 1.8)
        for i in range(g.size):
            for j in range(g.size):
                cell = g[i, j]
                color = self.controller.get_color(cell)
                x0 = i * cell_size
                y0 = j * cell_size
                x1 = (i + 1) * cell_size
                y1 = (j + 1) * cell_size

                # Draw rectangle
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="gray")

                # Draw text centered inside the rectangle
                text_x = (x0 + x1) / 2
                text_y = (y0 + y1) / 2

                # For example, display cell coordinates or any property
                x = self.controller.p.value_fct()[j][i]
                self.canvas.create_text(text_x, text_y, text=f"{x}", fill="black")

if __name__ == "__main__" :
    app = Visualizer()
    app.mainloop()