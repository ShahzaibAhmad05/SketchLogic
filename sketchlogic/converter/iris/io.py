def convert(io_results: list, scale_factor: float = 0.3) -> None:
    """
    Adds the io results to the output.
    """

    translation_x = -(io_results[0]["CenterX"] * scale_factor) + 900
    translation_y = -(io_results[0]["CenterY"] * scale_factor) + 1000

    for io in io_results:
        io["Rotation"] = float(io["Rotation"])

        io["X"] = _snap_to_grid(_translate(_scale(io["CenterX"], scale_factor), translation_x)) - 10
        io["Y"] = _snap_to_grid(_translate(_scale(io["CenterY"], scale_factor), translation_y)) - 10

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
