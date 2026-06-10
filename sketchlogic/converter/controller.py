import sketchlogic.converter.iris.gates as gates
import sketchlogic.converter.iris.wires as wiring
import sketchlogic.converter.iris.io as io_converter
import sketchlogic.converter.iris.straightener as straightener


def run(model_results: list, wires: list, io_results: list, debug: bool = False) -> list:
    """
    Controller for the converter module.
    """

    output = []

    gates.convert(model_results)
    io_converter.convert(io_results)

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
