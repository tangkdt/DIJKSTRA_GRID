import tkinter as tk
from dijkstras import DIJKSTRA_GRID, RANDOM_GRID 

class App(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.pack()

        self.w = 1000
        self.h = 190
        self.screen_h = None
        self.margin = 50
        self.root.geometry(f'{self.w}x{self.h}') # Set dimensions
        self.root.title("DIJKSTRA_GRID") 

        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(side="top", fill="x", expand=True)

        self.canvas = tk.Canvas(self.root, width=self.w, height=self.h, bg="white")
        self.canvas.pack(side="top", fill="both")
        
        self.n_entry = None
        self.low_entry = None
        self.high_entry = None
        self.submit_button = None
        self.cost_label = None
        self.animation = None
        self.total_animation_time = 1000 # 1 sec to draw path

        self.A = None
        self.n = None
        self.low = None
        self.high = None
        self.cell_s = None
        self.cell_t = None
        self.cell_size = None
        self.cell_center = None

        self.draw_menu()
    
    def draw_menu(self):
        n_entry_label = tk.Label(self.menu_frame, text="Enter N for NxN grid (Must be > 0)")
        self.n_entry = tk.Entry(self.menu_frame, width=self.w)
        n_entry_label.pack()
        self.n_entry.pack()

        low_entry_label = tk.Label(self.menu_frame, text="Enter low range for weight (Must be >= 0)")
        self.low_entry = tk.Entry(self.menu_frame, width=self.w)
        low_entry_label.pack()
        self.low_entry.pack()

        high_entry_label = tk.Label(self.menu_frame, text="Enter high range for weight")
        self.high_entry = tk.Entry(self.menu_frame, width=self.w)
        high_entry_label.pack()
        self.high_entry.pack()

        self.submit_button = tk.Button(self.menu_frame, text="Submit", command=self._on_submit)
        self.submit_button.pack()

        self.root.bind("<Return>", self._on_submit) # Form submission
        self.canvas.bind("<Motion>", self._on_hover) # Cell highlight
        self.canvas.bind("<Button-1>", self._on_click) # Selecting start cell

    def _on_submit(self, event=None):
        n = self.n_entry.get()
        low = self.low_entry.get()
        high = self.high_entry.get()
        if not all([n, low, high]): return

        n = int(n)
        low, high = int(low), int(high)

        if n <= 0:
            print("Invalid N (Must be positive int)")
            return

        if low < 0 or low > high: 
            print("Invalid range")
            return

        self.n = n
        self.low, self.high = low, high
        self.A = RANDOM_GRID(self.n, self.low, self.high)
        self.cell_s, self.cell_t = (0, 0), (self.n-1, self.n-1)
        self._resize_window()
        self._run_and_draw(new=True)

    # Sets new starting cell position on click
    def _on_click(self, event):
        if self.A is None: return 

        i = event.y // self.cell_size 
        j = event.x // self.cell_size
        if i >= self.n or j >= self.n: return

        self.cell_s = (i, j)
        self._run_and_draw()

    # Highlights a cell on hover
    def _on_hover(self, event):
        if self.cell_size is None: return 

        # Delete old highlight
        self.canvas.delete("highlighted_cell")

        i = event.y // self.cell_size 
        j = event.x // self.cell_size

        x0 = j * self.cell_size
        y0 = i * self.cell_size
        x1 = x0 + self.cell_size
        y1 = y0 + self.cell_size

        self.canvas.create_oval(
                                x0, y0, x1, y1,
                                outline="purple",
                                width=5,
                                tags="highlighted_cell"
                            )

    def _resize_window(self):
        self.root.update_idletasks()
        menu_h = self.menu_frame.winfo_height()  
        screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        avail_h = self.screen_h - menu_h - 200
        avail_w = screen_w

        self.cell_size = min(avail_w // self.n, avail_h // self.n)
        self.cell_center = self.cell_size // 2

        # Resize canvas to fit new grid
        grid_size = self.n * self.cell_size
        self.canvas.config(width=grid_size, height=grid_size)

    # Visualized the DIJKSTRA_GRID algorith from cell_s to cell_t 
    # on a NxN GRID A with weights between low and high
    def _run_and_draw(self, new=False):
        if new: self.canvas.delete("all") 
        self.canvas.delete("path")
        self.canvas.update_idletasks()

        # Run 
        min_cost, min_cell_path = DIJKSTRA_GRID(self.A, self.cell_s, self.cell_t)
        self.draw_grid()
        self.draw_path(min_cell_path)
        path_cost = sum(self.A[r][c] for (r, c) in min_cell_path[1:]) # Skip cost of start

        # Assert validity
        if min_cost == path_cost:
            output = f'This shortest path from {self.cell_s} to {self.cell_t} is valid! (min cost: {min_cost} == path cost: {path_cost})'
        else:
            output = f'This shortest path from {self.cell_s} to {self.cell_t} is invalid! (min cost: {min_cost} != path cost: {path_cost})'

        if self.cost_label:
            self.cost_label.config(text=output)
            self.cost_label.update_idletasks()

        if new:
            self.cost_label = tk.Label(
                                self.root, 
                                text=output, 
                                font=("Arial", 15),
                                bg="black", fg="white", 
                                padx=5, pady=5
                            )
            self.cost_label.pack(side="bottom")

            menu_h = self.menu_frame.winfo_height()
            cost_h = self.cost_label.winfo_height()
            grid_size = self.n * self.cell_size
            self.w = grid_size
            self.h = menu_h + grid_size + cost_h + 20
            self.root.geometry(f'{self.w}x{self.h}')
            self.root.update_idletasks()

    # Cuts low and high range into three color ranges: green, yellow, red
    def get_weight_color(self, num: int, low: int, high: int) -> str:
        third = (high - low) // 3

        if num < low + third: 
            color = "green"
        elif num < low + 2 * third:
            color = "yellow"
        else:
            color = "red"

        return color

    # Draws a 2D grid with weighted numbers and colors
    def draw_grid(self):
        for i in range(self.n):
            for j in range(self.n):
                x0 = j * self.cell_size
                y0 = i * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size

                w = 0 if (i, j) == self.cell_s else self.A[i][j]
                print(w)
                fill_color = self.get_weight_color(w, self.low, self.high)

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
                                     tags="path"
                                    )  
                        
        # Workaround for animation since using time.sleep() and .update() in loops would break things
        delay = self.total_animation_time // len(cell_path)
        self.animation = self.root.after(delay, lambda: self.animate_path(cell_path, k + 1))

def main():
    root = tk.Tk()
    app = App(root)
    app.mainloop()

main()