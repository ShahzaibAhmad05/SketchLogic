from pathlib import Path
import sketchlogic.model.inference as inference
import sketchlogic.model.testing as testing


def run(input_image_path: Path, debug: bool = False) -> tuple[list, int]:
    """
    Controller for the model module.
    """

    model_path = Path("sketchlogic/model/SketchLogic.pt")
    results, next_id = inference.run(input_image_path, model_path)

    if debug:
        image = testing.load_image(input_image_path)
        testing.draw_results(image, results)
        testing.save_image(image, Path("model_test.png"))
        testing.save_json(results, Path("model_test.json"))

    return results, next_id
