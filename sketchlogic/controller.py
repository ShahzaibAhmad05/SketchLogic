from pathlib import Path
import sketchlogic.model.controller
# import sketchlogic.wiring.controller
import json


def run(input_image_path: Path, output_json_path: Path) -> None:
    """
    Controller for the sketchlogic system.
    """

    model_results = sketchlogic.model.controller.run(input_image_path, debug=True)
    # circuit_json = sketchlogic.wiring.controller.run(input_image_path, model_results)

    with open(output_json_path, "w") as file:
        json.dump(model_results, file, indent=4)
