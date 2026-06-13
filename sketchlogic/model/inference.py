from pathlib import Path
from ultralytics.models import YOLO
import numpy


def run(image: numpy.ndarray, model_path: Path) -> tuple[list, int]:
    """
    Does inference on a single image file.

    Args:
        image (numpy.ndarray): The image to run inference on
        model_path (Path): The path to the model file

    Returns:
        tuple[list, int]: A tuple containing a list of dictionaries containing the inference results and the next ID
    """

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    model = YOLO(model_path)
    results = model.predict(image, iou=0.5, agnostic_nms=True)[0]

    if not results.boxes:
        return [], 1

    output = []
    next_id = 1

    for i in range(len(results.boxes.cls)):
        x, y, w, h = results.boxes.xywh[i].tolist()
        class_id = int(results.boxes.cls[i])

        class_name = class_to_name(class_id)
        rotation = class_to_rotation(class_id)

        gate = {
            "$id": str(next_id),
            "$type": class_name,
            "CenterX": float(x),
            "CenterY": float(y),
            "Width": float(w),
            "Height": float(h),
            "Rotation": rotation
        }
        next_id += 1

        if class_name == "NotGate":
            gate["Input"] = {
                "$id": str(next_id),
                "Type": "Input"
            }
            next_id += 1
        else:
            gate["Inputs"] = []

        gate["Output"] = {
            "$id": str(next_id),
            "Type": "Output"
        }
        next_id += 1

        output.append(gate)

    return output, next_id


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
    }[class_id // 4]


def class_to_rotation(class_id: int) -> int:
    """
    Converts a class ID to a rotation angle for the inference results.

    Args:
        class_id (int): The class ID

    Returns:
        int: The rotation angle
    """

    return round(class_id % 4) * 90
