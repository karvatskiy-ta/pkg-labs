import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import time

class RasterizationDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Rasterization Algorithms Demo")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True)
        
        # Create tabs
        self.step_by_step_tab = ttk.Frame(self.notebook)
        self.dda_tab = ttk.Frame(self.notebook)
        self.bresenham_line_tab = ttk.Frame(self.notebook)
        self.bresenham_circle_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.step_by_step_tab, text="Step-by-Step")
        self.notebook.add(self.dda_tab, text="DDA")
        self.notebook.add(self.bresenham_line_tab, text="Bresenham Line")
        self.notebook.add(self.bresenham_circle_tab, text="Bresenham Circle")
        
        # Setup each tab
        self.setup_step_by_step_tab()
        self.setup_dda_tab()
        self.setup_bresenham_line_tab()
        self.setup_bresenham_circle_tab()

    def setup_input_fields(self, parent, is_circle=False):
        input_frame = ttk.Frame(parent)
        input_frame.pack(pady=5)
        
        if not is_circle:
            ttk.Label(input_frame, text="Start X:").grid(row=0, column=0, padx=5)
            start_x = ttk.Entry(input_frame, width=10)
            start_x.grid(row=0, column=1, padx=5)
            
            ttk.Label(input_frame, text="Start Y:").grid(row=0, column=2, padx=5)
            start_y = ttk.Entry(input_frame, width=10)
            start_y.grid(row=0, column=3, padx=5)
            
            ttk.Label(input_frame, text="End X:").grid(row=0, column=4, padx=5)
            end_x = ttk.Entry(input_frame, width=10)
            end_x.grid(row=0, column=5, padx=5)
            
            ttk.Label(input_frame, text="End Y:").grid(row=0, column=6, padx=5)
            end_y = ttk.Entry(input_frame, width=10)
            end_y.grid(row=0, column=7, padx=5)
            
            return start_x, start_y, end_x, end_y
        else:
            ttk.Label(input_frame, text="Center X:").grid(row=0, column=0, padx=5)
            center_x = ttk.Entry(input_frame, width=10)
            center_x.grid(row=0, column=1, padx=5)
            
            ttk.Label(input_frame, text="Center Y:").grid(row=0, column=2, padx=5)
            center_y = ttk.Entry(input_frame, width=10)
            center_y.grid(row=0, column=3, padx=5)
            
            ttk.Label(input_frame, text="Radius:").grid(row=0, column=4, padx=5)
            radius = ttk.Entry(input_frame, width=10)
            radius.grid(row=0, column=5, padx=5)
            
            return center_x, center_y, radius

    def setup_plot(self, parent):
        fig, ax = plt.subplots(figsize=(6, 6))
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(pady=5)
        ax.grid(True)
        ax.set_aspect('equal')
        return fig, ax, canvas

    def setup_step_by_step_tab(self):
        start_x, start_y, end_x, end_y = self.setup_input_fields(self.step_by_step_tab)
        fig, ax, canvas = self.setup_plot(self.step_by_step_tab)
        
        def run_step_by_step():
            try:
                x1, y1 = int(start_x.get()), int(start_y.get())
                x2, y2 = int(end_x.get()), int(end_y.get())
                
                start_time = time.time()
                points = self.step_by_step_algorithm(x1, y1, x2, y2)
                end_time = time.time()
                
                ax.clear()
                ax.grid(True)
                for point in points:
                    ax.plot(point[0], point[1], 'bo')
                ax.plot([x1, x2], [y1, y2], 'r--', alpha=0.5)
                canvas.draw()
                
                messagebox.showinfo("Execution Time", 
                                  f"Step-by-Step Algorithm took {(end_time - start_time):.6f} seconds")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid integer coordinates")
        
        ttk.Button(self.step_by_step_tab, text="Run Algorithm", 
                   command=run_step_by_step).pack(pady=5)

    def setup_dda_tab(self):
        start_x, start_y, end_x, end_y = self.setup_input_fields(self.dda_tab)
        fig, ax, canvas = self.setup_plot(self.dda_tab)
        
        def run_dda():
            try:
                x1, y1 = int(start_x.get()), int(start_y.get())
                x2, y2 = int(end_x.get()), int(end_y.get())
                
                start_time = time.time()
                points = self.dda_algorithm(x1, y1, x2, y2)
                end_time = time.time()
                
                ax.clear()
                ax.grid(True)
                for point in points:
                    ax.plot(point[0], point[1], 'bo')
                ax.plot([x1, x2], [y1, y2], 'r--', alpha=0.5)
                canvas.draw()
                
                messagebox.showinfo("Execution Time", 
                                  f"DDA Algorithm took {(end_time - start_time):.6f} seconds")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid integer coordinates")
        
        ttk.Button(self.dda_tab, text="Run Algorithm", 
                   command=run_dda).pack(pady=5)

    def setup_bresenham_line_tab(self):
        start_x, start_y, end_x, end_y = self.setup_input_fields(self.bresenham_line_tab)
        fig, ax, canvas = self.setup_plot(self.bresenham_line_tab)
        
        def run_bresenham_line():
            try:
                x1, y1 = int(start_x.get()), int(start_y.get())
                x2, y2 = int(end_x.get()), int(end_y.get())
                
                start_time = time.time()
                points = self.bresenham_line_algorithm(x1, y1, x2, y2)
                end_time = time.time()
                
                ax.clear()
                ax.grid(True)
                for point in points:
                    ax.plot(point[0], point[1], 'bo')
                ax.plot([x1, x2], [y1, y2], 'r--', alpha=0.5)
                canvas.draw()
                
                messagebox.showinfo("Execution Time", 
                                  f"Bresenham Line Algorithm took {(end_time - start_time):.6f} seconds")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid integer coordinates")
        
        ttk.Button(self.bresenham_line_tab, text="Run Algorithm", 
                   command=run_bresenham_line).pack(pady=5)

    def setup_bresenham_circle_tab(self):
        center_x, center_y, radius = self.setup_input_fields(self.bresenham_circle_tab, True)
        fig, ax, canvas = self.setup_plot(self.bresenham_circle_tab)
        
        def run_bresenham_circle():
            try:
                x, y = int(center_x.get()), int(center_y.get())
                r = int(radius.get())
                
                start_time = time.time()
                points = self.bresenham_circle_algorithm(x, y, r)
                end_time = time.time()
                
                ax.clear()
                ax.grid(True)
                for point in points:
                    ax.plot(point[0], point[1], 'bo')
                
                # Plot ideal circle for comparison
                theta = np.linspace(0, 2*np.pi, 100)
                circle_x = x + r * np.cos(theta)
                circle_y = y + r * np.sin(theta)
                ax.plot(circle_x, circle_y, 'r--', alpha=0.5)
                canvas.draw()
                
                messagebox.showinfo("Execution Time", 
                                  f"Bresenham Circle Algorithm took {(end_time - start_time):.6f} seconds")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid integer coordinates")
        
        ttk.Button(self.bresenham_circle_tab, text="Run Algorithm", 
                   command=run_bresenham_circle).pack(pady=5)

    def step_by_step_algorithm(self, x1, y1, x2, y2):
        points = []
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        
        if steps == 0:
            return [(x1, y1)]
        
        x_increment = dx / steps
        y_increment = dy / steps
        
        x = x1
        y = y1
        
        for _ in range(steps + 1):
            points.append((round(x), round(y)))
            x += x_increment
            y += y_increment
        
        return points

    def dda_algorithm(self, x1, y1, x2, y2):
        points = []
        dx = x2 - x1
        dy = y2 - y1
        
        steps = max(abs(dx), abs(dy))
        
        if steps == 0:
            return [(x1, y1)]
        
        x_increment = dx / steps
        y_increment = dy / steps
        
        x = x1
        y = y1
        
        for _ in range(steps + 1):
            points.append((round(x), round(y)))
            x += x_increment
            y += y_increment
        
        return points

    def bresenham_line_algorithm(self, x1, y1, x2, y2):
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        x, y = x1, y1
        
        step_x = 1 if x2 > x1 else -1
        step_y = 1 if y2 > y1 else -1
        
        if dx > dy:
            p = 2 * dy - dx
            
            for _ in range(dx + 1):
                points.append((x, y))
                
                if p >= 0:
                    y += step_y
                    p -= 2 * dx
                
                x += step_x
                p += 2 * dy
        else:
            p = 2 * dx - dy
            
            for _ in range(dy + 1):
                points.append((x, y))
                
                if p >= 0:
                    x += step_x
                    p -= 2 * dy
                
                y += step_y
                p += 2 * dx
        
        return points

    def bresenham_circle_algorithm(self, xc, yc, r):
        points = []
        x = 0
        y = r
        d = 3 - 2 * r
        
        def plot_circle_points(xc, yc, x, y):
            points.extend([
                (xc + x, yc + y), (xc - x, yc + y),
                (xc + x, yc - y), (xc - x, yc - y),
                (xc + y, yc + x), (xc - y, yc + x),
                (xc + y, yc - x), (xc - y, yc - x)
            ])
        
        while y >= x:
            plot_circle_points(xc, yc, x, y)
            
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
            x += 1
        
        return points

if __name__ == "__main__":
    root = tk.Tk()
    app = RasterizationDemo(root)
    root.mainloop()