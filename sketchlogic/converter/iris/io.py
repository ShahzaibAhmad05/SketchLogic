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
        

def resize(io_results: list, scale_factor: float) -> None:
    """
    Resizes the model results to the scale factor.
    """

    for component in io_results:
        component["Width"] = 20
        component["Height"] = 20
        component["CenterX"] = _snap_to_grid(scale(component["CenterX"], scale_factor))
        component["CenterY"] = _snap_to_grid(scale(component["CenterY"], scale_factor))


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
