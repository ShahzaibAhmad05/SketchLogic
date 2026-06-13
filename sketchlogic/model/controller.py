from pathlib import Path
import sketchlogic.model.inference as inference
import sketchlogic.model.testing as testing
import numpy
import cv2


def run(input_image: numpy.ndarray, debug: bool = False) -> tuple[list, int]:
    """
    Controller for the model module.
    """

    if len(input_image.shape) == 2:
        input_image = cv2.cvtColor(input_image, cv2.COLOR_GRAY2BGR)

    model_path = Path("sketchlogic/model/SketchLogic.pt")
    results, next_id = inference.run(input_image, model_path)

    if debug:
        testing.draw_results(input_image, results)
        testing.save_image(input_image, Path("model_test.png"))
        testing.save_json(results, Path("model_test.json"))

    return results, next_id
