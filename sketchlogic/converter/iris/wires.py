def resize(wires: list, scale_factor: float) -> None:
    """
    Resizes the wire points to the scale factor.
    """

    for wire in wires:
        wire["Points"] = [
            (
                _snap_to_grid(scale(point[0], scale_factor)),
                _snap_to_grid(scale(point[1], scale_factor)),
            )
            for point in wire["Points"]
        ]


def clear(wires: list) -> None:
    """
    Adds the wires to the output.
    """

    for wire in wires:
        wire["Points"] = []


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
