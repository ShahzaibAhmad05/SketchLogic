from pathlib import Path
from model.infer.raw import infer
from model.infer.converter import convert_to_serializable_dict
import json


def run(input_image_path: Path, output_json_path: Path) -> None:
    """
    Runs this module.
    """

    model_path = Path("./model/SketchLogic.pt")

    results = infer(input_image_path, model_path)
    converted = convert_to_serializable_dict(results)

    with open(output_json_path, "w") as file:
        json.dump(converted, file, indent=4)
