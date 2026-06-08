from pathlib import Path
from model.infer.raw import infer
from model.infer.converter import convert_to_output


def run(input_image_path: Path) -> list:
    """
    Controller for the model module.
    """

    model_path = Path("./model/SketchLogic.pt")

    results = infer(input_image_path, model_path)
    converted = convert_to_output(results)

    return converted
