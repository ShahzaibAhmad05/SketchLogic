import sketchlogic.converter.iris.gates as gates
import sketchlogic.converter.iris.wires as wiring
import sketchlogic.converter.iris.io as io_converter
import sketchlogic.converter.iris.straightener as straightener
from pathlib import Path
import cv2


def run(model_results: list, wires: list, io_results: list, input_image_path: Path, debug: bool = False) -> list:
    """
    Controller for the converter module.
    """

    output = []

    w, h = 1000, 1000
    if input_image_path.exists():
        image = cv2.imread(str(input_image_path), cv2.IMREAD_GRAYSCALE)
        if image is not None:
            w, h = image.shape[:2]

    avg_dimension = (w + h) / 2
    num_components = len(model_results)
    scale_factor = (avg_dimension / 1000) * (0.2 * max(5, num_components))
    gates.convert(model_results, scale_factor)
    io_converter.convert(io_results, scale_factor)

    try:
        straightener.straighten(model_results, io_results, wires, space_factor=30)
    except Exception as e:
        if debug:
            print()
            print(f"sketchlogic.converter.controller:")
            print(f"Error straightening: ")
            print(e)

    wiring.convert(wires)

    for gate in model_results:
        output.append(gate)

    for io in io_results:
        output.append(io)

    for wire in wires:
        output.append(wire)

    return output
