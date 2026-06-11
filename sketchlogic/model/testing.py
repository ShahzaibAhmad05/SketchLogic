import cv2
import json
import numpy
from pathlib import Path


def load_image(image_path: Path) -> numpy.ndarray:
    """
    Loads the image into a numpy array.    
    """

    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"model.testing.load_image(): file not found {str(image_path)}.")

    return image


def draw_results(image: numpy.ndarray, results: list) -> None:
    """
    Draws the resulting boxes on the image. 

    Dependent on keys:
        CenterX, CenterY, Width, Height
    """

    for result in results:
        cx, cy, w, h = result["CenterX"], result["CenterY"], result["Width"], result["Height"]
        x = int(cx - w / 2)
        y = int(cy - h / 2)
        w = int(w)
        h = int(h)

        label = f'{result["$type"]} {result["Rotation"]}'

        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(image, label, (x + 6, y + 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 2)


def save_image(image: numpy.ndarray, save_path: Path) -> None:
    """
    Saves the image to the given path.
    """

    cv2.imwrite(str(save_path), image.astype(numpy.uint8))


def save_json(to_save: list | dict, save_path: Path) -> None:
    """
    Saves the given data to a JSON file.
    """

    with open(save_path, "w") as file:
        json.dump(to_save, file, indent=4)
