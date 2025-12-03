import heapq
import random
from pprint import pprint
import tkinter as tk

class App(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.pack()

        self.w = 1000
        self.h = 190
        self.margin = 184
        self.root.geometry(f'{self.w}x{self.h}') # Set dimensions
        self.root.title("DIJKSTRA_GRID") 

        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(side="top", fill="x")

        self.canvas = tk.Canvas(self.root, width=self.w, height=self.h, bg="white")
        self.canvas.pack(side="top", fill="both", expand=True)
        
        self.n_entry = None
        self.low_entry = None
        self.high_entry = None
        self.submit_button = None
        self.cost_label = None
        self.animation = None

        self.draw_menu()

    # Callback for submit button
    def submit(self):
        n = self.n_entry.get()
        low = self.low_entry.get()
        high = self.high_entry.get()

        if not all([n, low, high]): return

        n = int(n)
        low = int(low)
        high = int(high)

        if low > high or low < 0: 
            print("Invalid range")
            return

        self.draw_dijkstra_grid(n, low, high)
    
    def draw_menu(self):
        n_entry_label = tk.Label(self.menu_frame, text="Enter N for NxN grid")
        self.n_entry = tk.Entry(self.menu_frame, width=self.w)
        n_entry_label.pack()
        self.n_entry.pack()

        low_entry_label = tk.Label(self.menu_frame, text="Enter low range for weight (Must be > 0)")
        self.low_entry = tk.Entry(self.menu_frame, width=self.w)
        low_entry_label.pack()
        self.low_entry.pack()

        high_entry_label = tk.Label(self.menu_frame, text="Enter high range for weight")
        self.high_entry = tk.Entry(self.menu_frame, width=self.w)
        high_entry_label.pack()
        self.high_entry.pack()

        submit_button = tk.Button(self.menu_frame, text="Submit", command=self.submit)
        submit_button.pack()

        # Allow enter button to submit
        self.root.bind("<Return>", lambda event: self.submit())

    def draw_dijkstra_grid(self, n: int, low: int, high: int): 
        # Reset
        if self.cost_label: self.cost_label.destroy()
        self.canvas.delete("all") 
        self.canvas.update()

        # Update so that the height of the menu can be retrieved
        self.root.update_idletasks()
        menu_h = self.menu_frame.winfo_height()  

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        self.cell_size = min(screen_w // n, (screen_h - menu_h - self.margin) // n)
        self.cell_center = self.cell_size // 2

        # Resize canvas to fit new grid
        grid_w = grid_h = n * self.cell_size
        self.canvas.config(width=grid_w, height=grid_h)

        # Set window dimensions
        self.w = min(grid_w, screen_w)
        self.h = min(grid_h + menu_h + self.margin, screen_h)
        self.root.geometry(f'{self.w}x{self.h}')

        cell_s = (0, 0)
        cell_t = (n-1, n-1)

        A = RANDOM_GRID(n, low, high)
        pprint(A)

        min_cost, min_cell_path = DIJKSTRA_GRID(A, cell_s, cell_t)

        self.draw_grid(A, low,  high)
        self.draw_path(min_cell_path)

        path_cost = sum(A[i][j] for (i, j) in min_cell_path)
        valid = (min_cost == path_cost)
        
        if valid:
            output = f'This path is valid! (min_cost: {min_cost} == path_cost: {path_cost})'
        else:
            output = f'This path is invalid! (min_cost: {min_cost} != path_cost: {path_cost})'

        self.cost_label = tk.Label(self.root, 
                         text=output, 
                         font=("Arial", 20),
                         bg="black", fg="white", 
                         padx=5, pady=5
                        )
                        
        self.cost_label.pack(side="bottom")

    # Cuts low and high range into three colors: green, yellow, red
    def get_weight_color(num: int, low: int, high: int) -> str:
        third = (high - low) // 3

        if num < low + third: 
            color = "green"
        elif num < 2*third:
            color = "yellow"
        else:
            color = "red"

        return color

    # Draws a 2D grid with weighted numbers and colors
    def draw_grid(self, A: list, low: int, high: int):
        n = len(A)

        for i in range(n):
            for j in range(n):
                x0 = j * self.cell_size
                y0 = i * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size

                w = A[i][j]
                fill_color = App.get_weight_color(w, low, high)

                self.canvas.create_rectangle(x0, y0, x1, y1, 
                                             outline="black",
                                             fill=fill_color,
                                             width=5
                                            )

                self.canvas.create_text(
                            x0 + self.cell_center, 
                            y0 + self.cell_center, 
                            text=str(w)
                        )

    # Animates the drawing of the path
    def draw_path(self, cell_path: list[tuple[int, int]]):
        if self.animation:
            self.root.after_cancel(self.animation)
            self.animation = None

        self.animate_path(cell_path, 0)

    # Draws an individual frame of the path animation
    def animate_path(self, cell_path: list[tuple[int, int]], k: int):
        if k >= len(cell_path): 
            self.animation = None
            return 

        s = cell_path[0]
        t = cell_path[-1]

        i, j = cell_path[k]
        x0 = j * self.cell_size
        y0 = i * self.cell_size
        x1 = x0 + self.cell_size
        y1 = y0 + self.cell_size

        if (i, j) == s or (i, j) == t:
            color = "purple"
            width = 10
        else:
            color = "white"
            width = 8
        
        self.canvas.create_rectangle(x0, y0, x1, y1, 
                                     outline=color,
                                     width=width,
                                    )  
                        
        # Workaround for animation since using time.sleep() and .update() in loops would break things
        delay = 50
        self.animation = self.root.after(delay, lambda: self.animate_path(cell_path, k + 1))
        

# Creates a random nxn grid with each cell containing random weights between low and high in O(N^2)
def RANDOM_GRID(n: int, low: int, high: int) -> list[list[int]]:
    A = [0] * n

    for i in range(n):
        A[i] = []
        for _ in range(n):
            w = random.randint(low, high)
            A[i].append(w)

    A[0][0] = 0 # Ensure starting weight is 0

    return A

# 2D cell tuple -> 1D vertex index in O(1)
def CELL_TO_VERTEX(cell: tuple[int, int], n: int) -> int:
    i, j = cell[0], cell[1]
    return i * n + j # 2D -> 1D

# 1D vertex index -> 2D cell tuple in O(1)
def VERTEX_TO_CELL(v: int, n: int) -> tuple[int, int]:
    i = v // n
    j = v % n 
    return (i, j) 

# Converts 2D GRID to a graph adj list in O(N^2)
def GRID_TO_GRAPH(A: list[list]):
    G = {}

    n = len(A)

    # Neighbors are UP, DOWN, LEFT, RIGHT
    directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]

    for i in range(n):
        for j in range(n):
            u = CELL_TO_VERTEX((i, j), n)
            G[u] = []

            for dx, dy in directions:
                r = i + dy 
                c = j + dx

                # Inbounds
                if 0 <= r < n and 0 <= c < n:
                    v = CELL_TO_VERTEX((r, c), n)
                    w = A[r][c]
                    G[u].append((v, w))

    return G

# Follows PRED ptrs to create the shortest path in O(V)
def CONSTRUCT_VERTEX_PATH(PRED: list[int], s: int, t: int): 
    if not PRED: return []
    
    vertex_path = []

    v = t 
    while v != None and v != s:
        u = PRED[v]
        vertex_path.append(v)
        v = u

        # No path
        if v is None: return []
    
    vertex_path.append(s)
    vertex_path.reverse()
    
    return vertex_path

# Converts a path of vertices to the corresponding path of cell tuples in O(V)
def CONSTRUCT_CELL_PATH(vertex_path: list[int], n: int):
    cell_path = []

    for v in vertex_path:
        cell = VERTEX_TO_CELL(v, n)
        cell_path.append(cell)

    return cell_path

# Returns shortest vertex path and its cost from a graph from s to t in O((V+E)logV)
def DIJKSTRAS(G: dict[int, list[tuple[int, int]]], s: int, t: int): 
    V = len(G)
    DIST = V * [float('inf')] # O(V)
    PRED = V * [None] # O(V)

    DIST[s] = 0

    pq = []
    heapq.heappush(pq, (DIST[s], s))

    # O(V) * O(logV) + O(E) * O(logV) = O((V+E)logV)
    while pq:
        wuv, u = heapq.heappop(pq) # O(logV)

        # Skip stale entries (Since you cannot change priority)
        if wuv != DIST[u]: continue

        # O(E) * O(logV) = O(ElogV)
        for (v, w) in G[u]: 
            nd = DIST[u] + w

            # Tense edge
            if nd < DIST[v]:
                DIST[v] = nd # Relax
                PRED[v] = u 
                heapq.heappush(pq, (nd, v)) # O(logV)

    min_cost = DIST[t]
    min_path = CONSTRUCT_VERTEX_PATH(PRED, s, t)

    return min_cost, min_path

# Runs DIJKSTRA on an nxn grid O(N^2logN)
def DIJKSTRA_GRID(A: list[list], cell_s: tuple[int, int], cell_t: tuple[int, int]) -> tuple[int, list]:
    n = len(A)

    G = GRID_TO_GRAPH(A) # O(N^2)
    s = CELL_TO_VERTEX(cell_s, n) 
    t = CELL_TO_VERTEX(cell_t, n)

    # O((V+E)logV) where V = N^2 and E = O(N) (4 neighbors) -> O(N^2logN^2) = O(N^2 * 2logN) = O(N^2logN)
    min_cost, min_vertex_path = DIJKSTRAS(G, s, t) 
    min_cell_path = CONSTRUCT_CELL_PATH(min_vertex_path, n) # O(V)

    return min_cost, min_cell_path

def main():
    root = tk.Tk()
    app = App(root)
    app.mainloop()

main()