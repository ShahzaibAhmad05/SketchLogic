def convert(model_results: list, scale_factor: float = 0.3) -> None:
    """
    Adds the gates to the output.
    """

    translation_x = -(model_results[0]["CenterX"] * scale_factor) + 900
    translation_y = -(model_results[0]["CenterY"] * scale_factor) + 1000

    for gate in model_results:
        gate["Rotation"] = float(gate["Rotation"])

        if gate["$type"] == "NotGate":
            gate["X"] = _snap_to_grid(_translate(_scale(gate["CenterX"], scale_factor), translation_x)) - 20
            gate["Y"] = _snap_to_grid(_translate(_scale(gate["CenterY"], scale_factor), translation_y)) - 20
        else:
            multiplier = len(gate["Inputs"])
            gate["X"] = _snap_to_grid(_translate(_scale(gate["CenterX"], scale_factor), translation_x)) - (multiplier * 20)
            gate["Y"] = _snap_to_grid(_translate(_scale(gate["CenterY"], scale_factor), translation_y)) - (multiplier * 20)

        gate["X"] = float(gate["X"])
        gate["Y"] = float(gate["Y"])

        del gate["Width"]
        del gate["Height"]
        del gate["CenterX"]
        del gate["CenterY"]


def _snap_to_grid(x: int | float) -> float:
    """
    Snaps a value to the grid.
    """

    return round(x / 10) * 10


def _scale(x: float, scale_factor: float) -> float:
    """
    Scales a value by a multiplier.
    """

    return round(x * scale_factor)


def _translate(x: float, value: float) -> float:
    """
    Translates a value by a value.
    """ 

    return x + value
