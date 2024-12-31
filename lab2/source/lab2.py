import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import exiftool
from collections import OrderedDict

class ImageInfoViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Metadata Viewer")
        self.root.geometry("800x600")

        # Initialize ExifTool
        self.et = exiftool.ExifToolHelper(encoding="utf-8")
        
        self.images_info = []
        self.current_index = 0

        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Create buttons frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Button(self.button_frame, text="Select File", command=self.select_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Select Folder", command=self.select_folder).pack(side=tk.LEFT, padx=5)

        # Create navigation frame
        self.nav_frame = ttk.Frame(self.main_frame)
        self.nav_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        self.prev_button = ttk.Button(self.nav_frame, text="Previous", command=self.prev_image, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.page_label = ttk.Label(self.nav_frame, text="")
        self.page_label.pack(side=tk.LEFT, padx=10)

        self.next_button = ttk.Button(self.nav_frame, text="Next", command=self.next_image, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5)

        # Create jump to page frame
        self.jump_frame = ttk.Frame(self.main_frame)
        self.jump_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))

        ttk.Label(self.jump_frame, text="Go to image:").pack(side=tk.LEFT, padx=5)
        self.page_entry = ttk.Entry(self.jump_frame, width=10)
        self.page_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.jump_frame, text="Go", command=self.jump_to_page).pack(side=tk.LEFT, padx=5)

        # Create search frame
        self.search_frame = ttk.Frame(self.main_frame)
        self.search_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))

        # Create table
        self.tree = ttk.Treeview(self.main_frame, columns=("property", "value"), show="headings", height=25)
        self.tree.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree.heading("property", text="Property")
        self.tree.heading("value", text="Value")
        self.tree.column("property", width=300)
        self.tree.column("value", width=600)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Configure main_frame grid weights
        self.main_frame.grid_rowconfigure(4, weight=1)

    def get_image_info(self, filepath):
        try:
            metadata = self.et.get_metadata(filepath)[0]
            # Create ordered dict with important fields first
            important_fields = OrderedDict()
            important_fields['FileName'] = metadata.get('File:FileName')
            match metadata.get('File:FileType'):
                case 'PNG':
                    important_fields['ImageWidth'] = metadata.get('PNG:ImageWidth')
                    important_fields['ImageHeight'] = metadata.get('PNG:ImageHeight')
                    important_fields['Compression'] = metadata.get('PNG:Compression')
                    important_fields['BitDepth'] = metadata.get('PNG:BitDepth')
                    important_fields['ColorType'] = metadata.get('PNG:ColorType')
                case 'JPEG':
                    important_fields['ImageWidth'] = metadata.get('File:ImageWidth')
                    important_fields['ImageHeight'] = metadata.get('File:ImageHeight')
                    important_fields['XResolution'] = metadata.get('JFIF:XResolution')
                    important_fields['YResolution'] = metadata.get('JFIF:YResolution')
                    important_fields['ResolutionUnit'] = metadata.get('JFIF:ResolutionUnit')
                    important_fields['BitsPerSample'] = metadata.get('File:BitsPerSample')
                    important_fields['ColorComponents'] = metadata.get('File:ColorComponents')
                case 'GIF':
                    important_fields['ImageWidth'] = metadata.get('GIF:ImageWidth')
                    important_fields['ImageHeight'] = metadata.get('GIF:ImageHeight')
                    important_fields['ColorResolutionDepth'] = metadata.get('GIF:ColorResolutionDepth')
                    important_fields['BitsPerPixel'] = metadata.get('GIF:BitsPerPixel')
                case 'TIFF':
                    important_fields['ImageWidth'] = metadata.get('EXIF:ImageWidth')
                    important_fields['ImageHeight'] = metadata.get('EXIF:ImageHeight')
                    important_fields['XResolution'] = metadata.get('EXIF:XResolution')
                    important_fields['YResolution'] = metadata.get('EXIF:YResolution')
                    important_fields['ResolutionUnit'] = metadata.get('EXIF:ResolutionUnit')
                    important_fields['ColorSpace'] = metadata.get('ICC_Profile:ColorSpaceData')
                    important_fields['BitsPerSample'] = metadata.get('EXIF:BitsPerSample')
                    important_fields['SamplesPerPixel'] = metadata.get('EXIF:SamplesPerPixel')
                case 'BMP':
                    important_fields['ImageWidth'] = metadata.get('File:ImageWidth')
                    important_fields['ImageHeight'] = metadata.get('File:ImageHeight')
                    important_fields['PixelsPerMeterX'] = metadata.get('File:PixelsPerMeterX')
                    important_fields['PixelsPerMeterY'] = metadata.get('File:PixelsPerMeterY')
                    important_fields['Compression'] = metadata.get('File:Compression')
                    important_fields['BitDepth'] = metadata.get('File:BitDepth')
                case 'PCX':
                    important_fields['ImageWidth'] = metadata.get('File:ImageWidth')
                    important_fields['ImageHeight'] = metadata.get('File:ImageHeight')
                    important_fields['XResolution'] = metadata.get('File:XResolution')
                    important_fields['YResolution'] = metadata.get('File:YResolution')
                    important_fields['BitsPerPixel'] = metadata.get('File:BitsPerPixel')
                    
            return important_fields
        except Exception as e:
            messagebox.showerror("Error", f"Error reading metadata: {str(e)}")
            return None

    def update_table(self, info):
        self.tree.delete(*self.tree.get_children())
        if info:
            for key, value in info.items():
                if isinstance(value, (list, tuple)):
                    value = ', '.join(map(str, value))
                self.tree.insert("", "end", values=(key, value))

    def select_file(self):
        filetypes = (
            ("Image files", "*.jpg *.jpeg *.gif *.tif *.bmp *.png *.pcx"),
            ("All files", "*.*")
        )
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            info = self.get_image_info(filepath)
            if info:
                self.images_info = [info]
                self.current_index = 0
                self.update_display()

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.images_info = []
            supported_formats = {'.jpg', '.jpeg', '.gif', '.tif', '.bmp', '.png', '.pcx'}
            
            for filename in os.listdir(folder_path):
                if any(filename.lower().endswith(fmt) for fmt in supported_formats):
                    filepath = os.path.join(folder_path, filename)
                    info = self.get_image_info(filepath)
                    if info:
                        self.images_info.append(info)
            
            if self.images_info:
                self.current_index = 0
                self.update_display()
            else:
                messagebox.showinfo("Info", "No supported image files found in the selected folder")

    def update_display(self):
        if self.images_info:
            self.update_table(self.images_info[self.current_index])
            self.page_label.config(text=f"Image {self.current_index + 1} of {len(self.images_info)}")
            
            self.prev_button.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
            self.next_button.config(state=tk.NORMAL if self.current_index < len(self.images_info) - 1 else tk.DISABLED)

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()

    def next_image(self):
        if self.current_index < len(self.images_info) - 1:
            self.current_index += 1
            self.update_display()

    def jump_to_page(self):
        try:
            page = int(self.page_entry.get())
            if 1 <= page <= len(self.images_info):
                self.current_index = page - 1
                self.update_display()
            else:
                messagebox.showerror("Error", "Invalid page number")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")

    def __del__(self):
        # Clean up ExifTool
        if hasattr(self, 'et'):
            self.et.terminate()

def main():
    root = tk.Tk()
    app = ImageInfoViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()