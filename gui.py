import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import os
import sys
from daq_controller import DAQController
from image_processor import bmp_to_binary_array, pos2volx, pos2voly, get_bmp_dimensions, rotate

class LaserWriting:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LaserWriting Program")
        self.create_widgets()
        self.daq_controller = DAQController()
        self.is_scanning = False
        self.img_tk = None
        self.scan_image = None
        self.scan_draw = None

    def create_widgets(self):
        self.file_label = tk.Label(self.root, text="BMP File:")
        self.file_label.grid(row=0, column=0, padx=10, pady=10)

        self.file_entry = tk.Entry(self.root, width=50)
        self.file_entry.grid(row=0, column=1, padx=10, pady=10)

        self.browse_button = tk.Button(self.root, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        self.angle_label = tk.Label(self.root, text="Rotation Angle :")
        self.angle_label.grid(row=1, column=0, padx=10, pady=10)

        self.angle_entry = tk.Entry(self.root)
        self.angle_entry.grid(row=1, column=1, padx=10, pady=10)
        self.angle_entry.insert(0, "17")

        self.x_offset_label = tk.Label(self.root, text="X Offset:")
        self.x_offset_label.grid(row=2, column=0, padx=10, pady=10)

        self.x_offset_entry = tk.Entry(self.root)
        self.x_offset_entry.grid(row=2, column=1, padx=10, pady=10)

        self.y_offset_label = tk.Label(self.root, text="Y Offset:")
        self.y_offset_label.grid(row=3, column=0, padx=10, pady=10)

        self.y_offset_entry = tk.Entry(self.root)
        self.y_offset_entry.grid(row=3, column=1, padx=10, pady=10)

        self.x_range_label = tk.Label(self.root, text="X Range:")
        self.x_range_label.grid(row=4, column=0, padx=10, pady=10)

        self.x_range_entry = tk.Entry(self.root)
        self.x_range_entry.grid(row=4, column=1, padx=10, pady=10)

        self.y_range_label = tk.Label(self.root, text="Y Range:")
        self.y_range_label.grid(row=5, column=0, padx=10, pady=10)

        self.y_range_entry = tk.Entry(self.root)
        self.y_range_entry.grid(row=5, column=1, padx=10, pady=10)

        self.start_button = tk.Button(self.root, text="Start Scan", command=self.start_processing)
        self.start_button.grid(row=6, column=0, padx=10, pady=10)

        self.stop_button = tk.Button(self.root, text="Stop Scan", command=self.stop_processing)
        self.stop_button.grid(row=6, column=1, padx=10, pady=10)

        self.manual_x_label = tk.Label(self.root, text="Manual X:")
        self.manual_x_label.grid(row=7, column=0, padx=10, pady=10)

        self.manual_x_entry = tk.Entry(self.root)
        self.manual_x_entry.grid(row=7, column=1, padx=10, pady=10)
        self.manual_x_entry.insert(0,"0")

        self.manual_y_label = tk.Label(self.root, text="Manual Y:")
        self.manual_y_label.grid(row=8, column=0, padx=10, pady=10)


        self.manual_y_entry = tk.Entry(self.root)
        self.manual_y_entry.grid(row=8, column=1, padx=10, pady=10)
        self.manual_y_entry.insert(0,"0")

        self.manual_button = tk.Button(self.root, text="Set Position", command=self.set_manual_position)
        self.manual_button.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

        self.points_x_label = tk.Label(self.root, text="Number of Points in X: 0")
        self.points_x_label.grid(row=10, column=0, columnspan=3, padx=10, pady=10)

        self.points_y_label = tk.Label(self.root, text="Number of Points in Y: 0")
        self.points_y_label.grid(row=11, column=0, columnspan=3, padx=10, pady=10)

        self.scan_status_label = tk.Label(self.root, text="Current Scan Line: 0")
        self.scan_status_label.grid(row=12, column=0, columnspan=3, padx=10, pady=10)

        self.image_label = tk.Label(self.root)
        self.image_label.grid(row=13, column=0, columnspan=3, padx=10, pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp")])
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, file_path)
        self.load_image(file_path)
        self.update_points_label()

    def load_image(self, file_path):
        img = Image.open(file_path)
        img.thumbnail((400, 400))
        self.img_tk = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.img_tk)

        # Initialize scan image
        self.scan_image = Image.new('RGB', img.size, "black")
        self.scan_draw = ImageDraw.Draw(self.scan_image)

    def update_points_label(self):
        file_path = self.file_entry.get()
        if file_path:
            num_of_pts_x, num_of_pts_y = get_bmp_dimensions(file_path)
            self.points_x_label.config(text=f"Number of Points in X: {num_of_pts_x}")
            self.points_y_label.config(text=f"Number of Points in Y: {num_of_pts_y}")

            # 设置默认值
            self.x_offset_entry.delete(0, tk.END)
            self.x_offset_entry.insert(0, int(-num_of_pts_x // 20))
            self.y_offset_entry.delete(0, tk.END)
            self.y_offset_entry.insert(0, int(-num_of_pts_y // 20))
            self.x_range_entry.delete(0, tk.END)
            self.x_range_entry.insert(0, int(num_of_pts_x // 10))
            self.y_range_entry.delete(0, tk.END)
            self.y_range_entry.insert(0, int(num_of_pts_y // 10))

    def start_processing(self):
        file_path = self.file_entry.get()
        try:
            angle = float(self.angle_entry.get())
            x_offset = float(self.x_offset_entry.get())
            y_offset = float(self.y_offset_entry.get())
            x_range = float(self.x_range_entry.get())
            y_range = float(self.y_range_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for all fields.")
            return

        if not file_path:
            messagebox.showerror("No File", "Please select a BMP file.")
            return

        self.is_scanning = True
        self.process_image(file_path, angle, x_offset, y_offset, x_range, y_range)

    import sys

    def stop_processing(self):
        """
        Stop scanning, reset the hardware, clear the scan image, and exit the application.
        """
        sys.exit(0)


    def set_manual_position(self):
        try:
            x = float(self.manual_x_entry.get())
            y = float(self.manual_y_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for manual position.")
            return

        voltage_x = pos2volx(x)
        voltage_y = pos2voly(y)
        self.daq_controller.write_voltage(voltage_x, voltage_y)

    def process_image(self, file_path, angle, x_offset, y_offset, x_range, y_range):
        binary_array = bmp_to_binary_array(file_path)
        num_of_pts_x, num_of_pts_y = get_bmp_dimensions(file_path)

        for y in range(num_of_pts_y):
            if not self.is_scanning:
                break
            if y % 2 == 0:
                x_range_iter = range(num_of_pts_x)
            else:
                x_range_iter = range(num_of_pts_x - 1, -1, -1)

            for x in x_range_iter:
                if not self.is_scanning:
                    break
                value = binary_array[y, x]
                x_rotated, y_rotated = rotate(x_offset + x * x_range / num_of_pts_x, y_offset + y * y_range / num_of_pts_y, angle)
                voltage_x = pos2volx(x_rotated)
                voltage_y = pos2voly(y_rotated)
                self.daq_controller.write_voltage(voltage_x, voltage_y)
                self.daq_controller.start_scan(on=(value == 0))

            self.scan_status_label.config(text=f"Current Scan Line: {y + 1}")
            self.update_scan_image(y, num_of_pts_x, binary_array)
            self.root.update_idletasks()

    def update_scan_image(self, current_line=None, width=None, binary_array=None):
        if current_line is not None and width is not None and binary_array is not None:
            for x in range(width):
                if binary_array[current_line, x] == 1:
                    self.scan_draw.point((x, current_line), fill="white")
                else:
                    self.scan_draw.point((x, current_line), fill="black")

        self.scan_image_tk = ImageTk.PhotoImage(self.scan_image)
        self.image_label.config(image=self.scan_image_tk)

    def run(self):
        self.root.mainloop()
