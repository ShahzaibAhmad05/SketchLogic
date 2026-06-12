import cv2
import numpy


def detect_all(image: numpy.ndarray, min_side_length: int) -> list[numpy.ndarray]:
    """
    Detects the contours in the image.

    Args:
        image (numpy.ndarray): The image to detect the contours in.
        min_side_length (int): The minimum length of the side of the contour.

    Returns:
        list: The detected contours.
    """

    contours, _ = cv2.findContours(
        image, mode=cv2.RETR_LIST, 
        method=cv2.CHAIN_APPROX_NONE
    )

    return [c for c in contours if max(cv2.boundingRect(c)[2:]) >= min_side_length]
