def add(output: list, io_results: list) -> list:
    """
    Adds the io results to the output.
    """

    for io in io_results:
        io["Rotation"] = float(io["Rotation"])
        if io["$type"] == "Probe":
            io["Rotation"] = (io["Rotation"] + 180) % 360

        io["X"] = _snap_to_grid(_translate(_scale(io["CenterX"], 0.3), 700))
        io["Y"] = _snap_to_grid(_translate(_scale(io["CenterY"], 0.3), 700))

        del io["Width"]
        del io["Height"]
        del io["CenterX"]
        del io["CenterY"]

        output.append(io)

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
