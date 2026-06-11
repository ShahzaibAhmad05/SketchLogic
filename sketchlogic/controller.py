from pathlib import Path
import sketchlogic.model.controller
import sketchlogic.connector.controller
import sketchlogic.converter.controller
import json


def run(input_image_path: Path, output_json_path: Path) -> None:
    """
    Controller for the sketchlogic system.
    """

    model_results, next_id = sketchlogic.model.controller.run(input_image_path, debug=True)

    model_results, wires, io_results, next_id = sketchlogic.connector.controller.run(
        input_image_path, model_results, next_id, debug=True
    )

    output = sketchlogic.converter.controller.run(model_results, wires, io_results, input_image_path, debug=True)

    with open(output_json_path, "w") as file:
        json.dump(output, file, indent=4)

    print()
