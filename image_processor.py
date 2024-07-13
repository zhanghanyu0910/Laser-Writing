from PIL import Image
import numpy as np
import math


def bmp_to_binary_array(file_path, threshold=128):
    with Image.open(file_path) as img:
        img = img.convert('L')
        img_array = np.array(img)
        binary_array = (img_array >= threshold).astype(int)
    return binary_array


def pos2volx(value):
    result = value / 5
    return max(-10, min(10, result))


def pos2voly(value):
    result = value / 5
    return max(-10, min(10, result))


def get_bmp_dimensions(file_path):
    with Image.open(file_path) as img:
        width, height = img.size
    return width, height


def rotate(x, y, angle):
    radians = math.radians(angle)
    cos_angle = math.cos(radians)
    sin_angle = math.sin(radians)

    x_new = x * cos_angle - y * sin_angle
    y_new = x * sin_angle + y * cos_angle

    return x_new, y_new
