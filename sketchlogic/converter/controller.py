import sketchlogic.converter.iris.gates as gates
import sketchlogic.converter.iris.wires as wiring
import sketchlogic.converter.iris.io as io


def run(model_results: list, wires: list, io_results: list) -> list:
    """
    Controller for the converter module.
    """

    output = []

    output = gates.add(output, model_results)
    output = io.add(output, io_results)
    output = wiring.add(output, wires)

    return output
