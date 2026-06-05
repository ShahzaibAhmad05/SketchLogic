from pathlib import Path
from ultralytics.models import YOLO
import math


def infer(image_path: Path) -> list:
    """
    Does inference on a single image file.

    Args:
        image_path (Path): Path to the image file

    Returns:
        list: A list of dictionaries containing the inference results
    """

    model_path = Path("./runs/train/run/weights/best.pt")
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    model = YOLO(model_path)
    results = model.predict(image_path)[0]

    if results.obb is None:
        return []

    output = []
    for i in range(len(results.obb.cls)):
        x, y, w, h, r = results.obb.xywhr[i].tolist()

        img_h, img_w = results.orig_img.shape[:2]

        center_x, center_y = denormalize(x, y, img_w, img_h)
        width, height = denormalize(w, h, img_w, img_h)
        rotation = round(math.degrees(r))

        output.append({
            "class": class_to_name(int(results.obb.cls[i])),
            "confidence": results.obb.conf[i],
            "centerX": center_x, 
            "centerY": center_y,
            "width": width,
            "height": height,
            "rotation": rotation
        })

    return output


def class_to_name(class_id: int) -> str:
    """
    Converts a class ID to a class name for the inference results. This should be consistent with the YAML config file in the dataset that the model was trained with.

    Args:
        class_id (int): The class ID

    Returns:
        str: The class name
    """

    return {
        0: "AndGate",
        1: "OrGate",
        2: "NotGate",
        3: "NandGate",
        4: "NorGate",
        5: "XorGate",
        6: "XnorGate",
    }[class_id]


def denormalize(val1: float, val2: float, img_width: int, img_height: int) -> tuple[int, int]:
    """
    Denormalizes two values at a time from gate results.

    Args:
        val1 (float): 
        val2 (float): 
        width (int): Image width in pixels
        height (int): Image height in pixels

    Returns:
        tuple[int, int]: The denormalized values
    """

    return round(val1 * img_width), round(val2 * img_height)
