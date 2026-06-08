import cv2
import numpy


def detect_all(image: numpy.ndarray) -> list[numpy.ndarray]:
    """
    Detects the contours in the image.

    Args:
        image (numpy.ndarray): The image to detect the contours in.

    Returns:
        list: The detected contours.
    """

    contours, _ = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    return [c for c in contours if cv2.arcLength(c, closed=False) >= 10]
