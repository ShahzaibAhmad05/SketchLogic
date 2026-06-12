import cv2
import numpy


def detect_all(image: numpy.ndarray, min_length: int, corners_approximation: float) -> list[numpy.ndarray]:
    """
    Detects the contours in the image.

    Args:
        image (numpy.ndarray): The image to detect the contours in.
        min_length (int): The minimum length of the contour.
        corners_approximation (float): The approximation factor for the contour.

    Returns:
        list: The detected contours.
    """

    output = []

    contours, _ = cv2.findContours(
        image, mode=cv2.RETR_LIST, 
        method=cv2.CHAIN_APPROX_NONE
    )

    for contour in contours:
        contour = cv2.approxPolyDP(
            contour, closed=False,
            epsilon=corners_approximation * cv2.arcLength(contour, closed=False)
        )

        if max(cv2.boundingRect(contour)[2:]) >= min_length:
            output.append(contour)

    return output
