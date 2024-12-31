import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np

class ImageProcessor:
	def __init__(self):
		self.window = tk.Tk()
		self.window.title("Image Processing Demo")

		# Initialize variables
		self.original_image = None
		self.processed_image = None
		self.setup_gui()

	def setup_gui(self):
		# Buttons
		tk.Button(self.window, text="Load Image", command=self.load_image).pack(pady=5)
		tk.Button(self.window, text="Apply Median Filter", command=self.apply_median_filter).pack(pady=5)
		tk.Button(self.window, text="Apply Histogram Thresholding", command=self.apply_histogram_threshold).pack(pady=5)
		tk.Button(self.window, text="Apply Gradient Thresholding", command=self.apply_gradient_threshold).pack(pady=5)
		tk.Button(self.window, text="Apply Adaptive Thresholding", command=self.apply_adaptive_threshold).pack(pady=5)
		tk.Button(self.window, text="Save Result", command=self.save_image).pack(pady=5)

		# Image display labels
		self.original_label = tk.Label(self.window)
		self.original_label.pack(side=tk.LEFT, padx=10)
		self.processed_label = tk.Label(self.window)
		self.processed_label.pack(side=tk.RIGHT, padx=10)

	def load_image(self):
		file_path = filedialog.askopenfilename()
		if file_path:
			self.original_image = Image.open(file_path).convert('L')

		# Convert to grayscale
		self.display_images()

	def display_images(self):
		if self.original_image:
			# Display original image
			photo = ImageTk.PhotoImage(self.original_image)
			self.original_label.configure(image=photo)
			self.original_label.image = photo

		if self.processed_image:
			# Display processed image
			photo = ImageTk.PhotoImage(self.processed_image)
			self.processed_label.configure(image=photo)
			self.processed_label.image = photo

	def save_image(self):
		if self.processed_image:
			file_path = filedialog.asksaveasfilename(defaultextension=".png")
			if file_path:
				self.processed_image.save(file_path)

	def apply_median_filter(self):
		if self.original_image:
			# Convert image to numpy array
			img_array = np.array(self.original_image)
			height, width = img_array.shape
			result = np.zeros((height, width), dtype=np.uint8)

			# Apply 3x3 median filter
			for i in range(1, height-1):
				for j in range(1, width-1):
					neighborhood = []
					for k in range(-1, 2):
						for l in range(-1, 2):
							neighborhood.append(img_array[i+k, j+l])
					neighborhood.sort()
					result[i, j] = neighborhood[4]
					# Median of 9 values
			self.processed_image = Image.fromarray(result)
			self.display_images()

	def apply_histogram_threshold(self):
		if self.original_image:
			img_array = np.array(self.original_image)
			# Calculate histogram
			histogram = [0] * 256
			for pixel in img_array.flatten():
				histogram[pixel] += 1
			# Find threshold using Otsu's method
			total_pixels = img_array.size
			sum_all = sum(i * h for i, h in enumerate(histogram))
			sum_background = 0
			weight_background = 0
			max_variance = 0
			threshold = 0
			for t in range(256):
				weight_background += histogram[t]
				if weight_background == 0:
					continue
				weight_foreground = total_pixels - weight_background
				if weight_foreground == 0:
					break
				sum_background += t * histogram[t]
				mean_background = sum_background / weight_background
				mean_foreground = (sum_all - sum_background) / weight_foreground
				variance = weight_background * weight_foreground * (mean_background - mean_foreground) ** 2
				if variance > max_variance:
					max_variance = variance
					threshold = t

			# Apply threshold
			result = (img_array > threshold) * 255
			self.processed_image = Image.fromarray(result.astype(np.uint8))
			self.display_images()

	def apply_gradient_threshold(self):
		if self.original_image:
			img_array = np.array(self.original_image)
			height, width = img_array.shape
			result = np.zeros((height, width), dtype=np.uint8)

			# Calculate gradient magnitude using Sobel operators
			gradient_x = np.zeros((height, width))
			gradient_y = np.zeros((height, width))
			for i in range(1, height-1):
				for j in range(1, width-1):
					# Sobel x-direction
					gradient_x[i, j] = (img_array[i+1, j-1] + 2*img_array[i+1, j] + img_array[i+1, j+1]) - (img_array[i-1, j-1] + 2*img_array[i-1, j] + img_array[i-1, j+1])

					# Sobel y-direction
					gradient_y[i, j] = (img_array[i-1, j+1] + 2*img_array[i, j+1] + img_array[i+1, j+1]) - (img_array[i-1, j-1] + 2*img_array[i, j-1] + img_array[i+1, j-1])
			gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)

			# Threshold gradient magnitude
			threshold = np.mean(gradient_magnitude) * 1.5
			result = (gradient_magnitude > threshold) * 255
			self.processed_image = Image.fromarray(result.astype(np.uint8))
			self.display_images()

	def apply_adaptive_threshold(self):
		if self.original_image:
			img_array = np.array(self.original_image)
			height, width = img_array.shape
			result = np.zeros((height, width), dtype=np.uint8)
			window_size = 15
			c = 2

			# Constant subtracted from mean
			for i in range(height):
				for j in range(width):

					# Define local window boundaries
					y_start = max(0, i - window_size//2)
					y_end = min(height, i + window_size//2 + 1)
					x_start = max(0, j - window_size//2)
					x_end = min(width, j + window_size//2 + 1)

					# Calculate local mean
					window = img_array[y_start:y_end, x_start:x_end]
					local_mean = np.mean(window)

					# Apply threshold
					if img_array[i, j] > local_mean - c:
						result[i, j] = 255 
			self.processed_image = Image.fromarray(result)
			self.display_images()

	def run(self):
		self.window.mainloop()

if __name__ == "__main__":
	app = ImageProcessor()
	app.run()