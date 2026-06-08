from pathlib import Path
from ultralytics.models import YOLO


def run(image_path: Path, model_path: Path) -> list:
    """
    Does inference on a single image file.

    Args:
        image_path (Path): Path to the image file
        model_path (Path): Path to the model file

    Returns:
        list: A list of dictionaries containing the inference results
    """

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    model = YOLO(model_path)
    results = model.predict(image_path)[0]

    if not results.boxes:
        return []

    output = []
    next_id = 1

    for i in range(len(results.boxes.cls)):
        x, y, w, h = results.boxes.xywh[i].tolist()
        class_id = int(results.boxes.cls[i])

        class_name = class_to_name(class_id)
        rotation = class_to_rotation(class_id)

        output.append({
            "$id": str(next_id),
            "$type": class_name,
            "CenterX": int(x),
            "CenterY": int(y),
            "Width": int(w),
            "Height": int(h),
            "Rotation": rotation
        })

        next_id += 1

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
