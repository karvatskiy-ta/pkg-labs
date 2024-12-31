import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import math

class KVisualizerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("3D Letter K Visualizer")
        
        # Create main container
        self.container = tk.Frame(master)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 8))
        self.setup_subplots()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.container)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Control panel
        self.control_panel = tk.Frame(self.container)
        self.control_panel.grid(row=0, column=1, sticky="nsew")
        
        # Initialize transformation matrices
        self.reset_transforms()
        
        # Initialize vertices
        self.init_vertices()
        
        # View angles
        self.elevation = 30
        self.azimuth = 45
        
        self.setup_controls()
        self.update_plot()
        
    def setup_subplots(self):
        # 3D view
        self.ax3d = self.fig.add_subplot(221, projection='3d')
        # XY projection
        self.ax_xy = self.fig.add_subplot(222)
        # XZ projection
        self.ax_xz = self.fig.add_subplot(223)
        # YZ projection
        self.ax_yz = self.fig.add_subplot(224)
        
        self.fig.tight_layout()
        
    def init_vertices(self):
        self.vertices = np.array([
            # Vertical stem
            [0, 0, 0], [0, 4, 0],
            [0.5, 0, 0], [0.5, 4, 0],
            [0, 0, 0.5], [0, 4, 0.5],
            [0.5, 0, 0.5], [0.5, 4, 0.5],
            
            # Diagonal strokes
            [0.5, 2, 0], [3, 4, 0],
            [0.5, 2, 0.5], [3, 4, 0.5],
            [0.5, 2, 0], [3, 0, 0],
            [0.5, 2, 0.5], [3, 0, 0.5]
        ])
        
    def reset_transforms(self):
        self.translation = np.array([0., 0., 0.])
        self.rotation = np.array([0., 0., 0.])
        self.scaling = np.array([1., 1., 1.])
        
    def setup_controls(self):
        # Translation controls
        tk.Label(self.control_panel, text="Translation").pack()
        for axis in ['X', 'Y', 'Z']:
            frame = tk.Frame(self.control_panel)
            frame.pack()
            tk.Label(frame, text=f"{axis}:").pack(side=tk.LEFT)
            scale = tk.Scale(frame, from_=-5, to=5, orient=tk.HORIZONTAL, resolution=0.1,
                           command=lambda x, axis=axis: self.translate(axis, float(x)))
            scale.pack(side=tk.LEFT)
        
        # Rotation controls
        tk.Label(self.control_panel, text="Rotation").pack()
        for axis in ['X', 'Y', 'Z']:
            frame = tk.Frame(self.control_panel)
            frame.pack()
            tk.Label(frame, text=f"{axis}:").pack(side=tk.LEFT)
            scale = tk.Scale(frame, from_=0, to=360, orient=tk.HORIZONTAL,
                           command=lambda x, axis=axis: self.rotate(axis, float(x)))
            scale.pack(side=tk.LEFT)
        
        # Scale controls
        tk.Label(self.control_panel, text="Scale").pack()
        for axis in ['X', 'Y', 'Z']:
            frame = tk.Frame(self.control_panel)
            frame.pack()
            tk.Label(frame, text=f"{axis}:").pack(side=tk.LEFT)
            scale = tk.Scale(frame, from_=0.1, to=3.0, orient=tk.HORIZONTAL, resolution=0.1,
                           command=lambda x, axis=axis: self.scale(axis, float(x)))
            scale.set(1.0)
            scale.pack(side=tk.LEFT)
            
        # View angle controls
        tk.Label(self.control_panel, text="View Angles").pack()
        frame = tk.Frame(self.control_panel)
        frame.pack()
        tk.Label(frame, text="Elevation:").pack(side=tk.LEFT)
        self.elevation_scale = tk.Scale(frame, from_=0, to=90, orient=tk.HORIZONTAL,
                                      command=self.update_view)
        self.elevation_scale.set(30)
        self.elevation_scale.pack(side=tk.LEFT)
        
        frame = tk.Frame(self.control_panel)
        frame.pack()
        tk.Label(frame, text="Azimuth:").pack(side=tk.LEFT)
        self.azimuth_scale = tk.Scale(frame, from_=0, to=360, orient=tk.HORIZONTAL,
                                     command=self.update_view)
        self.azimuth_scale.set(45)
        self.azimuth_scale.pack(side=tk.LEFT)
        
        # Reset button
        tk.Button(self.control_panel, text="Reset", command=self.reset).pack()
        
    def transform_vertices(self):
        vertices = self.vertices.copy()
        
        # Apply scaling
        vertices *= self.scaling
        
        # Apply rotation
        rx, ry, rz = np.radians(self.rotation)
        
        # Rotation matrices
        Rx = np.array([[1, 0, 0],
                      [0, np.cos(rx), -np.sin(rx)],
                      [0, np.sin(rx), np.cos(rx)]])
        
        Ry = np.array([[np.cos(ry), 0, np.sin(ry)],
                      [0, 1, 0],
                      [-np.sin(ry), 0, np.cos(ry)]])
        
        Rz = np.array([[np.cos(rz), -np.sin(rz), 0],
                      [np.sin(rz), np.cos(rz), 0],
                      [0, 0, 1]])
        
        vertices = vertices @ Rx @ Ry @ Rz
        
        # Apply translation
        vertices += self.translation
        
        return vertices
        
    def update_plot(self):
        vertices = self.transform_vertices()
        
        # Clear all plots
        for ax in [self.ax3d, self.ax_xy, self.ax_xz, self.ax_yz]:
            ax.clear()
        
        # 3D plot
        self.ax3d.view_init(self.elevation, self.azimuth)
        self.plot_letter(self.ax3d, vertices, '3D')
        
        # XY projection
        self.plot_letter(self.ax_xy, vertices[:, [0, 1]], 'XY')
        
        # XZ projection
        self.plot_letter(self.ax_xz, vertices[:, [0, 2]], 'XZ')
        
        # YZ projection
        self.plot_letter(self.ax_yz, vertices[:, [1, 2]], 'YZ')
        
        self.canvas.draw()
        
    def plot_letter(self, ax, vertices, mode):
        if mode == '3D':
            for i in range(0, len(vertices), 2):
                ax.plot3D([vertices[i,0], vertices[i+1,0]],
                         [vertices[i,1], vertices[i+1,1]],
                         [vertices[i,2], vertices[i+1,2]], 'b-')
            
            # Draw coordinate axes
            ax.plot3D([0, 5], [0, 0], [0, 0], 'r-', label='X')
            ax.plot3D([0, 0], [0, 5], [0, 0], 'g-', label='Y')
            ax.plot3D([0, 0], [0, 0], [0, 5], 'b-', label='Z')
            
        else:
            for i in range(0, len(vertices), 2):
                ax.plot([vertices[i,0], vertices[i+1,0]],
                       [vertices[i,1], vertices[i+1,1]], 'b-')
            
            # Draw coordinate axes
            ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            
        ax.grid(True)
        ax.set_title(f'{mode} Projection')
        
    def translate(self, axis, value):
        idx = {'X': 0, 'Y': 1, 'Z': 2}[axis]
        self.translation[idx] = value
        self.update_plot()
        
    def rotate(self, axis, value):
        idx = {'X': 0, 'Y': 1, 'Z': 2}[axis]
        self.rotation[idx] = value
        self.update_plot()
        
    def scale(self, axis, value):
        idx = {'X': 0, 'Y': 1, 'Z': 2}[axis]
        self.scaling[idx] = value
        self.update_plot()
        
    def update_view(self, _):
        self.elevation = self.elevation_scale.get()
        self.azimuth = self.azimuth_scale.get()
        self.update_plot()
        
    def reset(self):
        self.reset_transforms()
        self.elevation_scale.set(30)
        self.azimuth_scale.set(45)
        self.update_plot()

def main():
    root = tk.Tk()
    app = KVisualizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()