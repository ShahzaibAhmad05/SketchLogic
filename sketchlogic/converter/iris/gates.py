def convert(model_results: list) -> None:
    """
    Adds the gates to the output.
    """

    for gate in model_results:
        gate["X"] = gate["CenterX"] - gate["Width"] / 2
        gate["Y"] = gate["CenterY"] - gate["Height"] / 2

        del gate["Width"]
        del gate["Height"]
        del gate["CenterX"]
        del gate["CenterY"]

        gate["Rotation"] = float(gate["Rotation"])
        gate["X"] = float(round(gate["X"]))
        gate["Y"] = float(round(gate["Y"]))
        

def resize(model_results: list, scale_factor: float, translate_x: float, translate_y: float) -> None:
    """
    Resizes the model results to the scale factor.
    """

    for component in model_results:
        comp_type = component["$type"]
        if not comp_type.endswith("Gate"):
            continue

        if comp_type == "NotGate":
            component["Width"] = 40
            component["Height"] = 40
        else:
            component["Width"] = len(component["Inputs"]) * 20
            component["Height"] = len(component["Inputs"]) * 20

        component["CenterX"] = _snap_to_grid(
            _translate(scale(component["CenterX"], scale_factor), translate_x)
        )
        component["CenterY"] = _snap_to_grid(
            _translate(scale(component["CenterY"], scale_factor), translate_y)
        )


def _snap_to_grid(x: int | float) -> float:
    """
    Snaps a value to the grid.
    """

    return round(x / 10) * 10


def scale(x: float, scale_factor: float) -> float:
    """
    Scales a value by a scale factor.
    """

    return round(x * scale_factor)


def _translate(x: float, value: float) -> float:
    """
    Translates a value by a value.
    """ 

    return x + value


def _get_min_length(model_results: list) -> float:
    """
    Gets the minimum length from the model results.
    """

    min_length = float('inf')

    for component in model_results:
        if component["$type"] == "NotGate":
            min_length = min(min_length, component["Width"], component["Height"])

        elif component["$type"].endswith("Gate"):
            min_length = min(min_length, component["Width"], component["Height"])

    return min_length
