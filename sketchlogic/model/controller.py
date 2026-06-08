from pathlib import Path
import sketchlogic.model.inference
import sketchlogic.model.testing


def run(input_image_path: Path, debug: bool = False) -> list:
    """
    Controller for the model module.
    """

    model_path = Path("sketchlogic/model/SketchLogic.pt")
    results = sketchlogic.model.inference.run(input_image_path, model_path)

    if debug:
        image = sketchlogic.model.testing.load_image(input_image_path)
        sketchlogic.model.testing.draw_results(image, results)
        sketchlogic.model.testing.save_image(image, Path("model_test.png"))

    return results
