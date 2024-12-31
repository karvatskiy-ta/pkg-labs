import tkinter as tk
from dataclasses import dataclass
import math

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Line:
    p1: Point
    p2: Point

class ClippingDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Line Clipping Demonstration")
        
        # Canvas setup
        self.canvas_width = 800
        self.canvas_height = 600
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(pady=10)
        
        # Initialize data
        self.segments = []
        self.clip_window = None
        self.scale_factor = 1
        
        # Setup controls
        self.setup_controls()
        
        # Draw coordinate system
        self.draw_coordinate_system()

    def setup_controls(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)
        
        tk.Button(control_frame, text="Load Data", command=self.load_data).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Clip (Cohen-Sutherland)", command=self.cohen_sutherland_clip).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Clip (Sutherland-Hodgman)", command=self.sutherland_hodgman_clip).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT, padx=5)

    def draw_coordinate_system(self):
        # Draw axes
        self.canvas.create_line(0, self.canvas_height / 2, self.canvas_width, self.canvas_height / 2, fill='gray')
        self.canvas.create_line(self.canvas_width / 2, 0, self.canvas_width / 2, self.canvas_height, fill='gray')
        
        # Draw grid
        for x in range(0, self.canvas_width, 50):
            self.canvas.create_line(x, 0, x, self.canvas_height, fill='lightgray')
        for y in range(0, self.canvas_height, 50):
            self.canvas.create_line(0, y, self.canvas_width, y, fill='lightgray')

    def transform_point(self, x, y):
        # Transform from world coordinates to screen coordinates
        screen_x = self.canvas_width / 2 + x * self.scale_factor
        screen_y = self.canvas_height / 2 - y * self.scale_factor
        return screen_x, screen_y

    def load_data(self):
        # Sample data (in practice, this would load from a file)
        self.segments = [
            Line(Point(-100, -50), Point(100, 50)),
            Line(Point(-80, 80), Point(80, -80)),
            Line(Point(0, -100), Point(0, 100))
        ]
        self.clip_window = [
            Point(-60, -40),
            Point(60, -40),
            Point(60, 40),
            Point(-60, 40)
        ]
        self.draw_scene()

    def draw_scene(self):
        self.clear_canvas()
        self.draw_coordinate_system()
        
        # Draw original segments
        for segment in self.segments:
            x1, y1 = self.transform_point(segment.p1.x, segment.p1.y)
            x2, y2 = self.transform_point(segment.p2.x, segment.p2.y)
            self.canvas.create_line(x1, y1, x2, y2, fill='blue')
        
        # Draw clipping window
        if self.clip_window:
            points = []
            for point in self.clip_window:
                x, y = self.transform_point(point.x, point.y)
                points.extend([x, y])
            self.canvas.create_polygon(points, outline='red', fill='', width=2)

    def compute_code(self, x, y, xmin, ymin, xmax, ymax):
        code = 0
        if x < xmin:
            code |= 1  # Left
        elif x > xmax:
            code |= 2  # Right
        if y < ymin:
            code |= 4  # Bottom
        elif y > ymax:
            code |= 8  # Top
        return code

    def cohen_sutherland_clip(self):
        if not self.clip_window:
            return
        
        xmin = min(p.x for p in self.clip_window)
        xmax = max(p.x for p in self.clip_window)
        ymin = min(p.y for p in self.clip_window)
        ymax = max(p.y for p in self.clip_window)
        
        clipped_segments = []
        
        for segment in self.segments:
            x1, y1 = segment.p1.x, segment.p1.y
            x2, y2 = segment.p2.x, segment.p2.y
            
            code1 = self.compute_code(x1, y1, xmin, ymin, xmax, ymax)
            code2 = self.compute_code(x2, y2, xmin, ymin, xmax, ymax)
            accept = False
            
            while True:
                if code1 == 0 and code2 == 0:
                    accept = True
                    break
                elif code1 & code2 != 0:
                    break
                else:
                    code_out = code1 if code1 != 0 else code2
                    if code_out & 1:  # Left
                        x = xmin
                        y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                    elif code_out & 2:  # Right
                        x = xmax
                        y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                    elif code_out & 4:  # Bottom
                        y = ymin
                        x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                    else:  # Top
                        y = ymax
                        x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                    
                    if code_out == code1:
                        x1, y1 = x, y
                        code1 = self.compute_code(x1, y1, xmin, ymin, xmax, ymax)
                    else:
                        x2, y2 = x, y
                        code2 = self.compute_code(x2, y2, xmin, ymin, xmax, ymax)
            
            if accept:
                clipped_segments.append(Line(Point(x1, y1), Point(x2, y2)))
        
        # Draw clipped segments
        for segment in clipped_segments:
            x1, y1 = self.transform_point(segment.p1.x, segment.p1.y)
            x2, y2 = self.transform_point(segment.p2.x, segment.p2.y)
            self.canvas.create_line(x1, y1, x2, y2, fill='green', width=2)

    def sutherland_hodgman_clip(self):
        if not self.clip_window:
            return
        
        def inside(p, cp1, cp2):
            return (cp2.x - cp1.x) * (p.y - cp1.y) > (cp2.y - cp1.y) * (p.x - cp1.x)

        def compute_intersection(p1, p2, cp1, cp2):
            dc = Point(cp1.x - cp2.x, cp1.y - cp2.y)
            dp = Point(p1.x - p2.x, p1.y - p2.y)
            n1 = cp1.x * cp2.y - cp1.y * cp2.x
            n2 = p1.x * p2.y - p1.y * p2.x
            n3 = 1.0 / (dc.x * dp.y - dc.y * dp.x)
            return Point(
                (n1 * dp.x - n2 * dc.x) * n3,
                (n1 * dp.y - n2 * dc.y) * n3
            )
        
        polygons = [[seg.p1, seg.p2] for seg in self.segments]
        clipped_polygons = []
        
        for polygon in polygons:
            output_list = polygon
            for i in range(len(self.clip_window)):
                cp1 = self.clip_window[i]
                cp2 = self.clip_window[(i + 1) % len(self.clip_window)]
                input_list = output_list
                output_list = []
                if not input_list:
                    continue
                s = input_list[-1]
                for e in input_list:
                    if inside(e, cp1, cp2):
                        if not inside(s, cp1, cp2):
                            output_list.append(compute_intersection(s, e, cp1, cp2))
                        output_list.append(e)
                    elif inside(s, cp1, cp2):
                        output_list.append(compute_intersection(s, e, cp1, cp2))
                    s = e
                if output_list:
                    clipped_polygons.append(output_list)
        
        for polygon in clipped_polygons:
            points = []
            for point in polygon:
                x, y = self.transform_point(point.x, point.y)
                points.extend([x, y])
            if len(points) >= 4:
                self.canvas.create_line(points, fill='green', width=2)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.draw_coordinate_system()

def main():
    root = tk.Tk()
    app = ClippingDemo(root)
    root.mainloop()

if __name__ == "__main__":
    main()
