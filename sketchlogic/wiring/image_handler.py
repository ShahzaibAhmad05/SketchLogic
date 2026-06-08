"""
Helper utils for image processing.
"""

import cv2
import numpy
from skimage.morphology import skeletonize as skimage_skeletonize
from pathlib import Path


def binarize(image: numpy.ndarray) -> numpy.ndarray:
    """
    Binarizes the image.

    Args:
        image (numpy.ndarray): The image to binarize.
    """

    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
    return binary


def skeletonize(image: numpy.ndarray) -> numpy.ndarray:
    """
    Skeletonizes the image.

    Args:
        image (numpy.ndarray): The image to skeletonize.
    """

    bool_image = image > 0
    skeleton = skimage_skeletonize(bool_image)

    return (skeleton * 255).astype(numpy.uint8)


def color_boxes(image: numpy.ndarray, boxes: list[dict], color: int) -> numpy.ndarray:
    """
    Color the boxes in the image.

    Args:
        image (numpy.ndarray): The image to color the boxes in.
        boxes (list): The boxes to color.
        color (int): The color to color the boxes in.

    Returns:
        numpy.ndarray: The image with the boxes colored in.
    """

    new_image = image.copy()

    for box in boxes:
        center_x, center_y, w, h = box["CenterX"], box["CenterY"], box["Width"], box["Height"]

        x = int(center_x - w / 2)
        y = int(center_y - h / 2)

        new_image[y:y+h, x:x+w] = color

    return new_image


def load_image(image_path: Path) -> numpy.ndarray:
    """
    Loads the image from the given path.
    """

    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Failed to read image from {str(image_path)}")

    return image


def save_image(image: numpy.ndarray, image_path: Path) -> None:
    """
    Saves the image to the given path.
    """

    cv2.imwrite(str(image_path), image.astype(numpy.uint8))


def draw_points(image: numpy.ndarray, wires: list) -> numpy.ndarray:
    """
    Draws points on the image.

    Args:
        image (numpy.ndarray): The image to draw the points on.
        wires (list): The wires to draw the points on.

    Returns:
        numpy.ndarray: The image with the points drawn on it.
    """

    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    for wire in wires:
        for point in wire["Points"]:
            cv2.circle(image, (point[0], point[1]), 5, (0, 0, 255), 2)

    return image


def bridge_gaps(image: numpy.ndarray, max_gap_size: int = 5) -> numpy.ndarray:
    """
    Bridges small gaps in the binary image before skeletonization.

    Args:
        image (numpy.ndarray): The binarized image (lines must be white/255).
        max_gap_size (int): The maximum gap size in pixels to bridge. 
                            If you have larger breaks, increase this number.

    Returns:
        numpy.ndarray: The healed image.
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max_gap_size, max_gap_size))
    healed_image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    
    return healed_image


def draw_boxes(image: numpy.ndarray, boxes: list) -> numpy.ndarray:
    """
    Draws boxes on the image.
    
    Args:
        image (numpy.ndarray): The image to draw the boxes on.
        boxes (list): The boxes to draw on the image.

    Returns:
        numpy.ndarray: The image with the boxes drawn on it.
    """

    for box in boxes:
        cx, cy, w, h = box["CenterX"], box["CenterY"], box["Width"], box["Height"]

        x = int(cx - w / 2)
        y = int(cy - h / 2)

        label = f'{box["$type"]} {box["Rotation"]}'

        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(image, label, (x + 6, y + 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 2)

    return image
