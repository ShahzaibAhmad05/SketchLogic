from pathlib import Path
import cv2
from image_handler import binarize, skeletonize, color_boxes
from results_handler import load_model_results, remove_entries
from converter import convert


def connect(image_path: Path, model_results_json_path: Path) -> list[dict]:
    """
    Connects the circuit based on the model results.

    Args:
        image_path (Path): Path to the image file
        model_results_json_path (Path): Path to the model results JSON file
        output_json_path (Path): Path to the output JSON file

    Returns:
        None
    """
    
    image = cv2.imread(image_path)
    if not image:
        raise ValueError(f"Failed to read image from {image_path}")

    image = binarize(image)
    image = skeletonize(image)

    results = load_model_results(model_results_json_path)
    color_boxes(image, results, color=0)

    return results
