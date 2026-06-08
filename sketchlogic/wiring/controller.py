from pathlib import Path
import sketchlogic.wiring.image_handler as image_handler
import sketchlogic.wiring.wiring as wiring
import sketchlogic.wiring.contour_handler as contour_handler
import sketchlogic.wiring.io as io
import sketchlogic.wiring.wire_connector as wire_connector


def run(input_image_path: Path, model_results: list, next_id: int) -> tuple[list, list, list, int]:
    """
    Controller for the wiring module. This adds wiring to the model results.

    Dependent on keys:
        CenterX, CenterY, Width, Height, Rotation

    Args:
        input_image_path (Path): Path to the input image.
        model_results (list): The model results to add wiring to.
        next_id (int): The next id to use for the wiring.

    Returns:
        tuple[list, list, list, int]: A tuple containing the model results, wires, io results, and the next id.
    """

    image = image_handler.load_image(input_image_path)

    image = image_handler.binarize(image)
    image = image_handler.bridge_gaps(image, max_gap_size=10)
    image = image_handler.skeletonize(image)

    wires_skeleton_image = image_handler.color_boxes(image, model_results, color=0)
    contours = contour_handler.detect_all(wires_skeleton_image)

    wires, next_id = wiring.generate(
        contours, next_id, 
        optional_min_length=100, 
        strict_min_length=30, 
        straightness_tolerance=15
    )
    wires, model_results, next_id = wire_connector.connect(wires, model_results, next_id, snapping_range=10)

    io_results, wires, next_id = io.generate(
        contours, wires, model_results, 
        next_id, min_bulkiness=20, 
        snapping_range=100
    )

    # model_results, next_id = wiring.generate(wires, model_results, next_id, snapping_range=30)
    # model_results = converter.remove_entries_from_gates(model_results, ["Width", "Height"])
    # model_results = converter.clear_wire_points(model_results)


    image = image_handler.draw_points(image, wires)
    image = image_handler.draw_boxes(image, model_results)
    image = image_handler.draw_boxes(image, io_results)

    image_handler.save_image(image, Path("output.png"))


    return model_results, wires, io_results, next_id
