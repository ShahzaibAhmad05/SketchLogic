import cv2
import numpy
from pathlib import Path


def load_image(image_path: Path) -> numpy.ndarray:
    """
    Loads the image from the given path into a numpy array.

    Args:
        image_path (Path): The path to the image, must exist.

    Returns:
        numpy.ndarray: The loaded image as a numpy array.

    Raises:
        FileNotFoundError: If the image file does not exist or failed to load.
    """

    if not image_path.exists():
        raise FileNotFoundError(f"processing.image.load_image(): file not found {str(image_path)}.")

    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"processing.image.load_image(): failed to read image from {str(image_path)}.")

    return image


def save_image(image: numpy.ndarray, save_path: Path) -> None:
    """
    Saves the image to the given path.

    Args:
        image (numpy.ndarray): The image to save.
        save_path (Path): The path to save the image to.
    """

    cv2.imwrite(str(save_path), image.astype(numpy.uint8))


def draw_component_boxes(
    image: numpy.ndarray,
    boxes: list[dict],
    box_color: tuple[int, int, int],
    font_color: tuple[int, int, int] | None = None,
) -> None:
    """
    Draws the resulting boxes on the image. 

    Args:
        image (numpy.ndarray): The image to draw the boxes on.
        boxes (list[dict]): The boxes to draw on the image. 
            Must include CenterX, CenterY, Width, Height, $type, Rotation.
        box_color (tuple[int, int, int]): The color of the boxes in BGR format.
        font_color (tuple[int, int, int] | None): The color of the font in BGR format. 
            If None, the box_color will be used.

    Raises:
        ValueError: If the boxes do not include the required keys.
    """

    if not all(
        all(key in box for key in ["CenterX", "CenterY", "Width", "Height", "$type", "Rotation"])
        for box in boxes
    ):
        raise ValueError(f"processing.image.draw_component_boxes(): boxes are missing required keys.")

    if font_color is None:
        font_color = box_color

    for box in boxes:
        cx, cy, w, h = box["CenterX"], box["CenterY"], box["Width"], box["Height"]

        x = int(cx - w / 2)
        y = int(cy - h / 2)

        w = int(w)
        h = int(h)

        label = f'{box["$type"]} {box["Rotation"]}'

        cv2.rectangle(image, (x, y), (x + w, y + h), box_color, 2)
        cv2.putText(image, label, (x + 6, y + 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, font_color, 2)
