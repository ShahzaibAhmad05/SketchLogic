import sketchlogic.converter.iris.gates as gate_converter
import sketchlogic.converter.iris.wires as wiring
import sketchlogic.converter.iris.io as io_converter
import sketchlogic.converter.iris.straightener as straightener
import sketchlogic.connector.image_handler as image_handler
import sketchlogic.converter.iris.scale_factor as scale_factor_calculator
import sketchlogic.converter.iris.translate_factor as translate_factor_calculator
from pathlib import Path


def run(model_results: list, wires: list, io_results: list, input_image_path: Path, debug: bool = False) -> list:
    """
    Controller for the converter module.

    NOTE: since translation is calculated based on the scale factor, it MUST be applied only after the
    scale factor is applied. This has to be fixed soon.
    """

    output = []

    scale_factor = scale_factor_calculator.calculate(model_results, per_component=80)
    translate_x, translate_y = translate_factor_calculator.calculate(
        model_results, scale_factor, center_x=1000, center_y=1000
    )

    gate_converter.resize(model_results, scale_factor, translate_x, translate_y)
    io_converter.resize(io_results, scale_factor, translate_x, translate_y)
    wiring.resize(wires, scale_factor, translate_x, translate_y)

    if debug:
        image = image_handler.load_image(input_image_path)
        image = image_handler.draw_points(image, wires)
        image = image_handler.draw_boxes(image, model_results)
        image = image_handler.draw_boxes(image, io_results)
        image_handler.save_image(image, Path("converter_test.png"))

    try:
        straightener.straighten(model_results, io_results, wires, space_factor=30, debug=debug)
    except Exception as e:
        if debug:
            print()
            print(f"sketchlogic.converter.controller:")
            print(f"Error straightening: {e}")

    gate_converter.convert(model_results)
    io_converter.convert(io_results)
    wiring.clear(wires)

    for gate in model_results:
        output.append(gate)
    for io in io_results:
        output.append(io)
    for wire in wires:
        output.append(wire)

    return output
