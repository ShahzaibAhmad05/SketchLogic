import sketchlogic.converter.iris.gates as gate_converter
import sketchlogic.converter.iris.wires as wiring
import sketchlogic.converter.iris.io as io_converter
import sketchlogic.converter.iris.straightener as straightener
import sketchlogic.connector.image_handler as image_handler
import sketchlogic.converter.iris.scale_factor as scale_factor_calculator
import sketchlogic.converter.iris.translate_factor as translate_factor_calculator
from pathlib import Path


def run(model_results: list, wires: list, io_results: list, debug: bool = False) -> list:
    """
    Controller for the converter module.

    NOTE: since translation is calculated based on the scale factor, it MUST be applied only after the
    scale factor is applied. This has to be fixed soon.
    """

    scale_factor = scale_factor_calculator.calculate(
        model_results, io_results, per_component=60, per_io=20
    )

    translate_x, translate_y = translate_factor_calculator.calculate(
        model_results, scale_factor, center_x=1000, center_y=1000
    )

    gate_converter.resize(model_results, scale_factor, translate_x, translate_y)
    io_converter.resize(io_results, scale_factor, translate_x, translate_y)
    wiring.resize(wires, scale_factor, translate_x, translate_y)

    if debug:
        image = image_handler.create_blank(width=2000, height=2000)
        image = image_handler.draw_points(image, wires, color=(255, 0, 0))
        image = image_handler.draw_boxes(image, model_results, color=(255, 0, 0))
        image = image_handler.draw_boxes(image, io_results, color=(255, 0, 0))
        image_handler.save_image(image, Path("converter_test.png"))

    try:
        straightener.straighten(model_results, io_results, wires, min_wire_length=30, debug=debug)
    except Exception as e:
        if debug:
            print()
            print(f"sketchlogic.converter.controller:")
            print(f"Error straightening: {e}")

    gate_converter.convert(model_results)
    io_converter.convert(io_results)
    wiring.clear(wires)

    return model_results + io_results + wires
