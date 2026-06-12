import cv2
from cv2.typing import MatLike
import numpy


def generate(
    contours: list[numpy.ndarray], 
    next_id: int, 
    optional_min_side: int, 
    strict_min_side: int,
    straightness_tolerance: float,
    debug: bool = False
) -> tuple[list, list, int]:
    """
    Filters the wires based on the minimum length and straightness.

    Args:
        contours (list[numpy.ndarray]): The contours to filter.
        optional_min_side (int): Allows for contours that are larger than this.
        strict_min_side (int): The strict minimum length of the wire.
        straightness_tolerance (float): The straightness tolerance of the wire.
        debug (bool): Whether to print debug information.

    Returns:
        tuple[list, list, int]: A tuple containing the filtered wires, discarded contours, and the next id.
        int: The next id to use for the circuit objects.
    """

    output = []
    discarded_contours = []

    for contour in contours:
        if not _has_minimum_side(contour, optional_min_side):
            if (not _has_minimum_side(contour, strict_min_side) or 
                not _straightness_test(contour, straightness_tolerance)):
                discarded_contours.append(
                    {"Points": [(int(pt[0][0]), int(pt[0][1])) for pt in contour]}
                )
                continue

        wire_points = [(int(pt[0][0]), int(pt[0][1])) for pt in contour]

        if _straightness_test(contour, straightness_tolerance) and len(wire_points) > 2:
            wire_points = remove_collinear_points(wire_points)

        output.append({
            "$id": str(next_id),
            "$type": "Wire",
            "Points": wire_points,
            "MainInput": {},
            "MainOutput": {}
        })
        next_id += 1

    if debug:
        print()
        print(f"sketchlogic.connector.wiring.generator:")
        print(f"Wires generated: {len(output)}")
        print(f"Discarded contours: {len(discarded_contours)}")

    return output, discarded_contours, next_id


def _has_minimum_side(contour: MatLike, min_side: int) -> bool:
    """
    Checks if the contour has a minimum length or width.

    Args:
        contour (MatLike): The contour to check.
        min_side (int): The minimum length of the side of the wire.

    Returns:
        bool: True if the contour has length OR width >= min_side, False otherwise.
    """

    _, _, w, h = cv2.boundingRect(contour)
    if w < min_side and h < min_side:
        return False

    return True


def _straightness_test(contour: MatLike, tolerance: float) -> bool:
    """
    Checks if the contour is straight enough.

    Args:
        contour (MatLike): The contour to check.
        tolerance (int): The tolerance threshold.

    Returns:
        bool: True if the contour min side <= tolerance, False otherwise.
    """

    _, _, w, h = cv2.boundingRect(contour)
    return min(w, h) <= tolerance


def remove_collinear_points(points: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Removes collinear points from a list of points.

    Args:
        points (list[tuple[int, int]]): The points to remove collinear points from.

    Returns:
        list[tuple[int, int]]: The points with collinear points removed.
    """

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    if max(xs) - min(xs) > max(ys) - min(ys):
        return [min(points, key=lambda p: p[0]), max(points, key=lambda p: p[0])]
    else:
        return [min(points, key=lambda p: p[1]), max(points, key=lambda p: p[1])]
