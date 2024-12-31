import tkinter as tk
from tkinter import ttk, messagebox
import colorsys
import numpy as np
from functools import partial

class ColorConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Space Converter")
        self.root.geometry("800x600")
        
        # Flag to prevent recursive updates
        self.updating = False
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Color display
        self.color_display = tk.Canvas(main_frame, width=200, height=200)
        self.color_display.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Create frames for each color model
        self.rgb_frame = self.create_model_frame(main_frame, "RGB", 1, 
                                               ["R", "G", "B"],
                                               [(0, 255), (0, 255), (0, 255)])
        
        self.cmyk_frame = self.create_model_frame(main_frame, "CMYK", 2,
                                                ["C", "M", "Y", "K"],
                                                [(0, 100), (0, 100), (0, 100), (0, 100)])
        
        self.lab_frame = self.create_model_frame(main_frame, "LAB", 3,
                                               ["L", "a", "b"],
                                               [(0, 100), (-128, 127), (-128, 127)])
        
        # Predefined colors palette
        self.create_palette(main_frame)
        
        # Approximation warning label
        self.warning_label = ttk.Label(main_frame, text="", foreground="red")
        self.warning_label.grid(row=5, column=0, columnspan=3)
        
        # Initialize with black
        self.update_from_rgb([0, 0, 0])

    def create_model_frame(self, parent, title, row, labels, ranges):
        frame = ttk.LabelFrame(parent, text=title, padding="5")
        frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        controls = []
        for i, (label, (min_val, max_val)) in enumerate(zip(labels, ranges)):
            ttk.Label(frame, text=label).grid(row=0, column=i*3)
            
            var = tk.DoubleVar()
            spinbox = ttk.Spinbox(frame, from_=min_val, to=max_val, width=5,
                                textvariable=var)
            spinbox.grid(row=0, column=i*3 + 1)
            spinbox.bind('<Return>', lambda e, t=title, idx=i: 
                        self.on_spinbox_change(t, idx))
            spinbox.bind('<FocusOut>', lambda e, t=title, idx=i: 
                        self.on_spinbox_change(t, idx))
            spinbox.bind('<<Increment>>', lambda e, t=title, idx=i: 
                        self.on_spinbox_change(t, idx))
            spinbox.bind('<<Decrement>>', lambda e, t=title, idx=i: 
                        self.on_spinbox_change(t, idx))
            
            slider = ttk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL,
                             variable=var)
            slider.grid(row=0, column=i*3 + 2, padx=5)
            slider.bind('<B1-Motion>', lambda e, t=title, idx=i: 
                       self.on_slider_change(t, idx))
            slider.bind('<Button-1>', lambda e, t=title, idx=i: 
                       self.on_slider_change(t, idx))
            
            controls.append((var, spinbox, slider))
        
        return controls

    def create_palette(self, parent):
        palette_frame = ttk.LabelFrame(parent, text="Predefined Colors", padding="5")
        palette_frame.grid(row=4, column=0, columnspan=3, pady=5)
        
        colors = ["red", "green", "blue", "yellow", "cyan", "magenta", "white", "black"]
        for i, color in enumerate(colors):
            btn = tk.Button(palette_frame, bg=color, width=3, height=1,
                          command=lambda c=color: self.on_palette_click(c))
            btn.grid(row=0, column=i, padx=2)

    def rgb_to_cmyk(self, rgb):
        r, g, b = [x/255 for x in rgb]
        k = 1 - max(r, g, b)
        if k == 1:
            return [0, 0, 0, 100]
        c = (1-r-k)/(1-k) * 100
        m = (1-g-k)/(1-k) * 100
        y = (1-b-k)/(1-k) * 100

        return [c, m, y, k*100]

    def cmyk_to_rgb(self, cmyk):
        c, m, y, k = [x/100 for x in cmyk]
        r = 255 * (1-c) * (1-k)
        g = 255 * (1-m) * (1-k)
        b = 255 * (1-y) * (1-k)

        return [round(r), round(g), round(b)]

    def rgb_to_lab(self, rgb):
        # RGB to XYZ
        r, g, b = [x/255 for x in rgb]
        
        def transform(x):
            return x/12.92 if x <= 0.04045 else ((x + 0.055)/1.055) ** 2.4
        
        r, g, b = transform(r), transform(g), transform(b)
        
        x = 0.4124564 * r + 0.3575761 * g + 0.1804375 * b
        y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
        z = 0.0193339 * r + 0.1191920 * g + 0.9503041 * b
        
        # XYZ to Lab
        xn, yn, zn = 0.95047, 1.00000, 1.08883
        
        def f(t):
            return t**(1/3) if t > 0.008856 else 7.787*t + 16/116
        
        fx = f(x/xn)
        fy = f(y/yn)
        fz = f(z/zn)
        
        L = max(0, min(100, 116 * fy - 16))
        a = max(-128, min(127, 500 * (fx - fy)))
        b = max(-128, min(127, 200 * (fy - fz)))
        
        self.warning_label.config(text="")

        return [L, a, b]

    def lab_to_rgb(self, lab):
        L, a, b = lab
        
        # Lab to XYZ
        fy = (L + 16) / 116
        fx = a / 500 + fy
        fz = fy - b / 200
        
        def f_inv(t):
            return t**3 if t > 0.206893 else (t - 16/116) / 7.787
        
        xn, yn, zn = 0.95047, 1.00000, 1.08883
        x = xn * f_inv(fx)
        y = yn * f_inv(fy)
        z = zn * f_inv(fz)
        
        # XYZ to RGB
        r = 3.2404542 * x - 1.5371385 * y - 0.4985314 * z
        g = -0.9692660 * x + 1.8760108 * y + 0.0415560 * z
        b = 0.0556434 * x - 0.2040259 * y + 1.0572252 * z
        
        def transform(x):
            return x * 12.92 if x <= 0.0031308 else 1.055 * x**(1/2.4) - 0.055
        
        r, g, b = transform(r), transform(g), transform(b)
        
        # Clamp values
        rgb = [max(0, min(255, round(x * 255))) for x in [r, g, b]]
        
        # Check if conversion was approximate
        original_lab = self.rgb_to_lab(rgb)
        if any(abs(x - y) > 1 for x, y in zip(lab, original_lab)):
            self.warning_label.config(text="Note: Some color values are approximate due to conversion limitations")
        else:
            self.warning_label.config(text="")
            
        return rgb

    def update_display(self, rgb):
        rounded_rgb = [round(x) for x in rgb]
        hex_color = "#{:02x}{:02x}{:02x}".format(*rounded_rgb)
        self.color_display.delete("all")
        self.color_display.create_rectangle(0, 0, 200, 200, fill=hex_color, outline="")

    def update_controls(self, rgb, cmyk, lab):
        if not self.updating:
            self.updating = True
            
            # Update RGB controls
            for i, value in enumerate(rgb):
                self.rgb_frame[i][0].set(value)
            
            # Update CMYK controls
            for i, value in enumerate(cmyk):
                self.cmyk_frame[i][0].set(value)
            
            # Update LAB controls
            for i, value in enumerate(lab):
                self.lab_frame[i][0].set(value)
                
            self.updating = False

    def update_from_rgb(self, rgb):
        cmyk = self.rgb_to_cmyk(rgb)
        lab = self.rgb_to_lab(rgb)
        self.update_controls(rgb, cmyk, lab)
        self.update_display(rgb)

    def update_from_cmyk(self, cmyk):
        rgb = self.cmyk_to_rgb(cmyk)
        lab = self.rgb_to_lab(rgb)
        self.update_controls(rgb, cmyk, lab)
        self.update_display(rgb)

    def update_from_lab(self, lab):
        rgb = self.lab_to_rgb(lab)
        cmyk = self.rgb_to_cmyk(rgb)
        self.update_controls(rgb, cmyk, lab)
        self.update_display(rgb)

    def on_spinbox_change(self, model, index):
        if self.updating:
            return
            
        if model == "RGB":
            values = [self.rgb_frame[i][0].get() for i in range(3)]
            self.update_from_rgb(values)
        elif model == "CMYK":
            values = [self.cmyk_frame[i][0].get() for i in range(4)]
            self.update_from_cmyk(values)
        else:  # LAB
            values = [self.lab_frame[i][0].get() for i in range(3)]
            self.update_from_lab(values)

    def on_slider_change(self, model, index):
        if self.updating:
            return
            
        if model == "RGB":
            values = [self.rgb_frame[i][0].get() for i in range(3)]
            self.update_from_rgb(values)
        elif model == "CMYK":
            values = [self.cmyk_frame[i][0].get() for i in range(4)]
            self.update_from_cmyk(values)
        else:  # LAB
            values = [self.lab_frame[i][0].get() for i in range(3)]
            self.update_from_lab(values)

    def on_palette_click(self, color):
        # Convert color name to RGB
        self.root.update()
        rgb = [int(self.root.winfo_rgb(color)[i]/256) for i in range(3)]
        self.update_from_rgb(rgb)

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorConverterApp(root)
    root.mainloop()