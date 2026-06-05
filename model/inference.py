from pathlib import Path
from ultralytics.models import YOLO


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
    results = model.predict(image_path)

    return results
