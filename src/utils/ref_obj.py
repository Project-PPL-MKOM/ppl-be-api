import cv2
import numpy as np


def detect_ref_obj(image):
    # Convert the image to the HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for the green color
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])

    # Create a mask for the green color
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Apply morphological operations to remove noise and enhance contours
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Find contours
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Find the largest contour
        ruler_contour = max(contours, key=cv2.contourArea)
        return ruler_contour
    else:
        print("Penggaris hijau tidak ditemukan")


def get_contour_length(contour, image_shape):
    # Get the four corner points of the ruler
    rect = cv2.minAreaRect(contour)

    # Get the width and height of the rectangle
    width = int(rect[1][0])
    height = int(rect[1][1])

    # Determine the longer dimension
    long_dimension = max(width, height)

    # Calculate the height in Cartesian coordinates
    length_cartesian = long_dimension / image_shape[0]

    return length_cartesian
