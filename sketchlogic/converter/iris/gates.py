def add(output: list, model_results: list) -> list:
    """
    Adds the gates to the output.
    """

    for gate in model_results:
        gate["Rotation"] = float(gate["Rotation"])

        gate["X"] = _snap_to_grid(_translate(_scale(gate["CenterX"], 0.3), 700))
        gate["Y"] = _snap_to_grid(_translate(_scale(gate["CenterY"], 0.3), 700))

        del gate["Width"]
        del gate["Height"]
        del gate["CenterX"]
        del gate["CenterY"]

        output.append(gate)

    return output


def _snap_to_grid(x: int | float) -> float:
    """
    Snaps a value to the grid.
    """

    return round(x / 10) * 10


def _scale(x: float, multiplier: float) -> float:
    """
    Scales a value by a multiplier.
    """

    return round(x * multiplier)


def _translate(x: float, value: float) -> float:
    """
    Translates a value by a value.
    """ 

    return x + value
