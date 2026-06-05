from pathlib import Path
from ultralytics.models import YOLO
import json


def infer(image_path: Path, output_path: Path) -> None:
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

    with open(output_path / "results.json", "w") as file:
        json.dump(results, file, indent=4)
