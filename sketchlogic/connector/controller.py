from pathlib import Path
import sketchlogic.connector.image_handler as image_handler
import sketchlogic.connector.wiring.generator
import sketchlogic.connector.wiring.connector
import sketchlogic.connector.contour_handler as contour_handler
import sketchlogic.connector.io_generator as io_generator
import numpy


def run(image: numpy.ndarray, model_results: list, next_id: int, debug: bool = False) -> tuple[list, list, list, int]:
    """
    Controller for the wiring module. This adds wiring to the model results.

    Dependent on keys:
        CenterX, CenterY, Width, Height, Rotation

    Args:
        image (numpy.ndarray): The image to add wiring to.
        model_results (list): The model results to add wiring to.
        next_id (int): The next id to use for the wiring.

    Returns:
        tuple[list, list, list, int]: A tuple containing the model results, wires, io results, and the next id.
    """

    image = image_handler.binarize(image, offset=100, non_dark_offset=150, debug=debug)
    image = image_handler.bridge_gaps(image, max_gap_size=10)
    image = image_handler.skeletonize(image)

    wires_skeleton_image = image_handler.color_boxes(image, model_results, color=0)

    contours = contour_handler.detect_all(
        wires_skeleton_image, min_length=30, 
        corners_approximation=0.03
    )

    wires, discarded_contours, next_id = sketchlogic.connector.wiring.generator.generate(
        contours, next_id, 
        optional_min_side=80, 
        strict_min_side=30, 
        straightness_tolerance=25,
        debug=debug
    )

    removed_wires, next_id = sketchlogic.connector.wiring.connector.connect(
        wires, model_results, next_id, 
        max_range=25, debug=debug
    )

    io_results, next_id = io_generator.generate(
        wires, model_results, next_id, debug=debug
    )

    if debug:
        image = image_handler.draw_points(image, wires, color=(200, 0, 0))
        image = image_handler.draw_points(image, discarded_contours, color=(0, 0, 100))
        image = image_handler.draw_points(image, removed_wires, color=(0, 0, 200))

        image = image_handler.draw_boxes(image, model_results, color=(200, 0, 0))
        image = image_handler.draw_boxes(image, io_results, color=(200, 0, 0))

        image_handler.save_image(image, Path("connector_test.png"))

        print()
        print(f"sketchlogic.connector.controller:")
        print(f"Contours detected: {len(contours)}")
        print(f"Wires detected: {len(wires)}")
        print(f"IOs detected: {len(io_results)}")

    return model_results, wires, io_results, next_id
