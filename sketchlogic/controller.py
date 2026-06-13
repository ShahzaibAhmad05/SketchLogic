from pathlib import Path
import sketchlogic.model.controller
import sketchlogic.connector.controller
import sketchlogic.converter.controller
import sketchlogic.processing.image as image_processing
import json


def run(input_image_path: Path, output_json_path: Path) -> None:
    """
    Controller for the sketchlogic system.
    """

    image = image_processing.load(input_image_path)
    image = image_processing.enhance(image)

    if True:
        image_processing.save(image, Path("enhancer_test.png"))

    model_results, next_id = sketchlogic.model.controller.run(image, debug=True)

    model_results, wires, io_results, next_id = sketchlogic.connector.controller.run(
        image, model_results, next_id, debug=True
    )

    output = sketchlogic.converter.controller.run(model_results, wires, io_results, debug=True)

    with open(output_json_path, "w") as file:
        json.dump(output, file, indent=4)

    print()
