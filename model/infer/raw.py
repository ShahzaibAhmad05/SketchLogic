from pathlib import Path
from ultralytics.models import YOLO
import math


def infer(image_path: Path, model_path: Path) -> list:
    """
    Does inference on a single image file.

    Args:
        image_path (Path): Path to the image file

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
    for i in range(len(results.boxes.cls)):
        x, y, w, h = results.boxes.xywh[i].tolist()

        output.append({
            "Class": int(results.boxes.cls[i]),
            "Confidence": float(results.boxes.conf[i]),
            "CenterX": int(x),
            "CenterY": int(y),
            "Width": int(w),
            "Height": int(h)
        })

    return output
