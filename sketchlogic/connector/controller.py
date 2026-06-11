from pathlib import Path
import sketchlogic.connector.image_handler as image_handler
import sketchlogic.connector.wiring.generator
import sketchlogic.connector.wiring.connector
import sketchlogic.connector.contour_handler as contour_handler
import sketchlogic.connector.io_generator as io_generator


def run(input_image_path: Path, model_results: list, next_id: int, debug: bool = False) -> tuple[list, list, list, int]:
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
    image = image_handler.binarize(image, offset=100, non_dark_offset=150, debug=debug)
    image = image_handler.bridge_gaps(image, max_gap_size=10)
    image = image_handler.skeletonize(image)

    wires_skeleton_image = image_handler.color_boxes(image, model_results, color=0)
    contours = contour_handler.detect_all(wires_skeleton_image, min_side_length=30)

    wires, next_id = sketchlogic.connector.wiring.generator.generate(
        contours, next_id, 
        optional_min_side=200, 
        strict_min_side=30, 
        straightness_tolerance=25
    )

    next_id = sketchlogic.connector.wiring.connector.connect(
        wires, model_results, next_id, 
        max_range=25, debug=debug
    )

    io_results, next_id = io_generator.generate(
        wires, model_results, next_id, debug=debug
    )

    if debug:
        image = image_handler.draw_points(image, wires)
        image = image_handler.draw_boxes(image, model_results)
        image = image_handler.draw_boxes(image, io_results)
        image_handler.save_image(image, Path("connector_test.png"))

        print()
        print(f"sketchlogic.connector.controller:")
        print(f"Contours detected: {len(contours)}")
        print(f"Wires detected: {len(wires)}")
        print(f"IOs detected: {len(io_results)}")

    return model_results, wires, io_results, next_id
