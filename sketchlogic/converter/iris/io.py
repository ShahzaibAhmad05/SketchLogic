def convert(io_results: list) -> None:
    """
    Adds the io results to the output.
    """

    for io in io_results:
        io["Rotation"] = float(io["Rotation"])

        io["X"] = _snap_to_grid(_translate(_scale(io["CenterX"]), 830)) - 10
        io["Y"] = _snap_to_grid(_translate(_scale(io["CenterY"]), 800)) - 10

        io["X"] = float(io["X"])
        io["Y"] = float(io["Y"])

        del io["Width"]
        del io["Height"]
        del io["CenterX"]
        del io["CenterY"]


def _snap_to_grid(x: int | float) -> float:
    """
    Snaps a value to the grid.
    """

    return round(x / 10) * 10


def _scale(x: float, multiplier: float = 0.3) -> float:
    """
    Scales a value by a multiplier.
    """

    return round(x * multiplier)


def _translate(x: float, value: float) -> float:
    """
    Translates a value by a value.
    """

    return x + value
