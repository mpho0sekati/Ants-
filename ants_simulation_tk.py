import tkinter as tk
from tkinter import ttk
from ants_simulation import AntSimulation

CELL_SIZE = 30
PADDING = 2

class AntsTkApp:
    def __init__(self, root):
        self.root = root
        root.title("Ant Simulation - Tkinter")
        self.sim = AntSimulation(width=20, height=10, num_ants=8, food_sources=4)
        self.running = False
        self.delay_ms = 150

        self.canvas = tk.Canvas(root, width=self.sim.width * CELL_SIZE, height=self.sim.height * CELL_SIZE, bg='white')
        self.canvas.grid(row=0, column=0, columnspan=4)
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<Button-3>', self.on_right_click)

        self.start_btn = ttk.Button(root, text="Start", command=self.toggle_running)
        self.start_btn.grid(row=1, column=0, sticky='ew')

        self.step_btn = ttk.Button(root, text="Step", command=self.step_once)
        self.step_btn.grid(row=1, column=1, sticky='ew')

        self.reset_btn = ttk.Button(root, text="Reset", command=self.reset_sim)
        self.reset_btn.grid(row=1, column=2, sticky='ew')

        self.speed = tk.IntVar(value=self.delay_ms)
        self.speed_slider = ttk.Scale(root, from_=20, to=500, variable=self.speed, command=self.on_speed_change)
        self.speed_slider.grid(row=1, column=3, sticky='ew')

        self.info_label = ttk.Label(root, text="Left click to add food, right click to spawn an enemy.")
        self.info_label.grid(row=2, column=0, columnspan=4, sticky='ew')

        self.rects = [[None for _ in range(self.sim.width)] for _ in range(self.sim.height)]
        self.draw_grid()
        self.update_canvas()

    def on_speed_change(self, _=None):
        self.delay_ms = int(self.speed.get())

    def reset_sim(self):
        self.sim = AntSimulation(width=self.sim.width, height=self.sim.height, num_ants=self.sim.num_ants, food_sources=0)
        self.draw_grid()
        self.update_canvas()

    def toggle_running(self):
        self.running = not self.running
        self.start_btn.config(text="Pause" if self.running else "Start")
        if self.running:
            self.root.after(self.delay_ms, self.loop)

    def step_once(self):
        self.sim.step()
        self.update_canvas()

    def loop(self):
        if not self.running:
            return
        self.sim.step()
        self.update_canvas()
        self.root.after(self.delay_ms, self.loop)

    def cell_to_pixel(self, x, y):
        x1 = x * CELL_SIZE + PADDING
        y1 = y * CELL_SIZE + PADDING
        x2 = (x + 1) * CELL_SIZE - PADDING
        y2 = (y + 1) * CELL_SIZE - PADDING
        return x1, y1, x2, y2

    def draw_grid(self):
        for y in range(self.sim.height):
            for x in range(self.sim.width):
                x1, y1, x2, y2 = self.cell_to_pixel(x, y)
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill='white', outline='#cccccc')
                self.rects[y][x] = rect

    def pheromone_color(self, value, max_val):
        if max_val <= 0:
            return '#ffffff'
        intensity = int(255 * min(1.0, value / max_val))
        r = 255
        g = 255 - int(intensity * 0.6)
        b = 255 - intensity
        return f'#{r:02x}{g:02x}{b:02x}'

    def update_canvas(self):
        max_p = 0
        for row in self.sim.pheromone_map:
            for v in row:
                if v > max_p:
                    max_p = v

        for y in range(self.sim.height):
            for x in range(self.sim.width):
                rect = self.rects[y][x]
                if (x, y) == (self.sim.home_x, self.sim.home_y):
                    color = '#99ccff'
                elif self.sim.food_map[y][x] > 0:
                    color = '#88cc88'
                else:
                    color = self.pheromone_color(self.sim.pheromone_map[y][x], max_p)
                self.canvas.itemconfig(rect, fill=color)

        self.canvas.delete('ant')
        for ant in self.sim.ants:
            x1, y1, x2, y2 = self.cell_to_pixel(ant.x, ant.y)
            color = 'blue' if ant.role == 'protector' else 'red'
            self.canvas.create_oval(x1+6, y1+6, x2-6, y2-6, fill=color, tags='ant')

        self.canvas.delete('enemy')
        for e in self.sim.enemies:
            x1, y1, x2, y2 = self.cell_to_pixel(e.x, e.y)
            self.canvas.create_rectangle(x1+8, y1+8, x2-8, y2-8, fill='black', tags='enemy')

        self.root.title(f"Ant Simulation - Step {self.sim.steps}  HomeHP={self.sim.home_health}")

    def on_click(self, event):
        x = event.x // CELL_SIZE
        y = event.y // CELL_SIZE
        if 0 <= x < self.sim.width and 0 <= y < self.sim.height:
            self.sim.food_map[y][x] += 1
            self.update_canvas()

    def on_right_click(self, event):
        x = event.x // CELL_SIZE
        y = event.y // CELL_SIZE
        if 0 <= x < self.sim.width and 0 <= y < self.sim.height:
            self.sim.spawn_enemy(x, y, health=5)
            self.update_canvas()


def main():
    root = tk.Tk()
    app = AntsTkApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
