"""
Helper utils for image processing.
"""

import cv2
import numpy
from skimage.morphology import h_minima, skeletonize as skimage_skeletonize


def binarize(image: numpy.ndarray) -> numpy.ndarray:
    """
    Binarizes the image.

    Args:
        image (numpy.ndarray): The image to binarize.
    """

    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    return binary


def skeletonize(image: numpy.ndarray) -> numpy.ndarray:
    """
    Skeletonizes the image.

    Args:
        image (numpy.ndarray): The image to skeletonize.
    """

    return skimage_skeletonize(image)


def color_boxes(image: numpy.ndarray, boxes: list[dict], color: int) -> None:
    """
    Color the boxes in the image.

    Args:
        image (numpy.ndarray): The image to color the boxes in.
        boxes (list): The boxes to color.
        color (int): The color to color the boxes in.
    """

    for box in boxes:
        center_x, center_y, w, h = box["centerX"], box["centerY"], box["width"], box["height"]

        x = center_x - w / 2
        y = center_y - h / 2

        image[y:y+h, x:x+w] = color
