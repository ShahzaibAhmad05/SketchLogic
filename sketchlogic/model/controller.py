from pathlib import Path
import sketchlogic.model.inference as inference
import sketchlogic.model.utils as utils
import numpy
import cv2
import sys


def run(input_image: numpy.ndarray, debug: bool = False) -> tuple[list, int]:
    """
    Controller for the model module.
    """

    if len(input_image.shape) == 2:
        input_image = cv2.cvtColor(input_image, cv2.COLOR_GRAY2BGR)

    model_path = _model_path()
    results, next_id = inference.run(input_image, model_path)

    if debug:
        utils.draw_results(input_image, results)
        utils.save_image(input_image, Path("model_test.png"))
        utils.save_json(results, Path("model_test.json"))

    return results, next_id


def _model_path() -> Path:
    """
    Returns the path to the model file.
    """

    meipass = getattr(sys, "_MEIPASS", None)

    if meipass:
        return Path(meipass) / "SketchLogic.pt"
    return Path("sketchlogic/model/SketchLogic.pt")
