def convert(io_results: list) -> None:
    """
    Adds the io results to the output.
    """

    for io in io_results:
        io["X"] = io["CenterX"] - io["Width"] / 2
        io["Y"] = io["CenterY"] - io["Height"] / 2

        del io["Width"]
        del io["Height"]
        del io["CenterX"]
        del io["CenterY"]

        io["Rotation"] = float(io["Rotation"])
        io["X"] = float(io["X"])
        io["Y"] = float(io["Y"])
        

def resize(io_results: list, scale_factor: float, translate_x: float, translate_y: float) -> None:
    """
    Resizes the io results to the scale factor.
    """

    for component in io_results:
        component["Width"] = 20
        component["Height"] = 20
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
