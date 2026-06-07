from pathlib import Path
from connector.handlers import image_handler, results_handler
from connector.fillers import wiring
import json


def run(input_image_path: Path, model_results_json_path: Path, output_json_path: Path) -> None:
    """
    Runs this module.
    """

    image = image_handler.load_image(input_image_path)
    model_results = results_handler.load_model_results(model_results_json_path)

    image = image_handler.binarize(image)
    image = image_handler.bridge_gaps(image, max_gap_size=10)
    image = image_handler.skeletonize(image)

    wires_image = image_handler.color_boxes(image, model_results, color=0)
    wires = wiring.detect_wires(wires_image, min_wire_length=80, straightness_tolerance=6)
    model_results = wiring.generate(wires, model_results, snapping_range=30)


    image_handler.save_image(image_handler.draw_points(image, wires), Path("output.png"))


    # results = connect(input_image_path, model_results_json_path)
    # converted_results = convert(results)

    with open(output_json_path, "w") as file:
        json.dump(model_results, file, indent=4)
