from pathlib import Path
import cv2
from cv2.typing import MatLike
import numpy
import math


def detect_wires(image: numpy.ndarray, min_wire_length: int, straightness_tolerance: int) -> list:
    """
    Detects the wires in the logic circuit.

    Args:
        image (numpy.ndarray): The image to detect the wires in.
        min_wire_length (int): The minimum length of the wire.
        straightness_tolerance (int): The tolerance threshold for the straightness of the wire.

    Returns:
        list: The detected wires.
    """

    contours, _ = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    wires = []

    for contour in contours:
        arc_length = cv2.arcLength(contour, closed=False)
        if arc_length < 10:
            continue

        if (not _has_minimum_length(contour, min_wire_length) and 
            not _is_collinear(contour, straightness_tolerance)):
            continue

        # Ramer-Douglas-Peucker algo
        points = cv2.approxPolyDP(contour, 0.015 * arc_length, closed=False)
        wire = [(int(pt[0][0]), int(pt[0][1])) for pt in points]

        wires.append(wire)

    return wires


def generate(contours: list, gate_results: list, snapping_range: int) -> list:
    """
    Attaches the wires to the gates.
    
    Args:
        wires (list): The wires to attach to the gates.
        gate_results (list): The results of the gates.
        discard_unattached (bool): Whether to discard the wires that are not attached to any gate.

    Returns:
        list: The attached wires.
    """

    next_id = len(gate_results) + 1
    new_wires = []

    for contour in contours:
        wire_id = next_id
        next_id += 1

        points = []
        for x, y in contour:
            points.append({
                "$id": next_id,
                "X": float(x),
                "Y": float(y),
            })
            next_id += 1

        new_wires.append({
            "$id": wire_id,
            "$type": "Wire",
            "Points": points,
            "MainInput": {},
            "MainOutput": {}
        })

    used_wire_ids = set()
    for gate in gate_results:
        gate_type = gate["$type"]

        center_x = gate["CenterX"]
        center_y = gate["CenterY"]
        width = gate["Width"]
        height = gate["Height"]
        rotation = gate["Rotation"]

        input_attached = False      # performance optimization
        output_attached = False

        if gate_type != "NotGate":
            gate["Inputs"] = []

        input_side = get_input_line(center_x, center_y, width, height, rotation)
        output_side = get_output_line(center_x, center_y, width, height, rotation)

        for wire in new_wires:
            if (not (gate["$type"] == "NotGate" and input_attached) and 
                _wire_near_line(wire["Points"], input_side[0], input_side[1], snapping_range)):

                if gate["$type"] == "NotGate":
                    gate["Input"] = {
                        "$id": next_id,
                        "Type": "Input"
                    }
                    wire["MainInput"]["$ref"] = next_id

                    used_wire_ids.add(wire["$id"])
                    input_attached = True
                    next_id += 1

                else:
                    gate["Inputs"].append({
                        "$id": next_id,
                        "Type": "Input"
                    })
                    wire["MainInput"]["$ref"] = next_id

                    used_wire_ids.add(wire["$id"])
                    next_id += 1

            elif (not output_attached and 
                _wire_near_line(wire["Points"], output_side[0], output_side[1], snapping_range)):

                gate["Output"] = {
                    "$id": next_id,
                    "Type": "Output"
                }
                wire["MainOutput"]["$ref"] = next_id

                used_wire_ids.add(wire["$id"])
                output_attached = True
                next_id += 1

    for wire in new_wires:
        if wire["$id"] in used_wire_ids:
            gate_results.append(wire)

    return gate_results


def _has_minimum_length(contour: MatLike, min_wire_length: int) -> bool:
    """
    Checks if the contour has a minimum length or width.

    Args:
        contour (MatLike): The contour to check.
        min_wire_length (int): The minimum length of the wire.

    Returns:
        bool: True if the contour has length / width >= min_wire_length, False otherwise.
    """

    _, _, wire_width, wire_height = cv2.boundingRect(contour)
    if wire_width < min_wire_length and wire_height < min_wire_length:
        return False

    return True


def _is_collinear(contour: MatLike, straightness_tolerance: int) -> bool:
    """
    Checks if the contour is collinear.

    Args:
        contour (MatLike): The contour to check.
        straightness_tolerance (int): The tolerance threshold.

    Returns:
        bool: True if the contour is collinear, False otherwise.
    """

    points = contour[:, 0, :].astype(numpy.float64)

    if len(points) <= 1:
        return False
    elif len(points) == 2:
        return True

    p1 = tuple(points[0])
    p2 = tuple(points[-1])
    distance = [_point_to_line_distance(tuple(point), p1, p2) for point in points]

    return max(distance) <= straightness_tolerance


def get_input_line(center_x: int, center_y: int, width: int, height: int, rotation: int) -> tuple:
    """
    Gets the input line of a gate.

    Args:
        center_x (int): The x coordinate of the center of the gate.
        center_y (int): The y coordinate of the center of the gate.
        width (int): The width of the gate.
        height (int): The height of the gate.
        rotation (int): The rotation of the gate.

    Returns:
        tuple: A tuple of two points that represent the input line.
    """

    x = center_x - width / 2
    y = center_y - height / 2

    if rotation == 0:
        return (x, y), (x, y + height)
    elif rotation == 90:
        return (x, y), (x + width, y)
    elif rotation == 180:
        return (x + width, y), (x + width, y + height)
    elif rotation == 270:
        return (x, y + height), (x + width, y + height)
    else:
        raise ValueError(f"connector.fillers.wiring.get_input_line: Bad value for rotation {rotation}")


def get_output_line(center_x: int, center_y: int, width: int, height: int, rotation: int) -> tuple:
    """
    Gets the output line of a gate.

    Args:
        center_x (int): The x coordinate of the center of the gate.
        center_y (int): The y coordinate of the center of the gate.
        width (int): The width of the gate.
        height (int): The height of the gate.
        rotation (int): The rotation of the gate.

    Returns:
        tuple: A tuple of two points that represent the input line.
    """

    x = center_x - width / 2
    y = center_y - height / 2

    if rotation == 0:
        return (x + width, y), (x + width, y + height)
    elif rotation == 90:
        return (x, y + height), (x + width, y + height)
    elif rotation == 180:
        return (x, y), (x, y + height)
    elif rotation == 270:
        return (x, y), (x + width, y)
    else:
        raise ValueError(f"connector.fillers.wiring.get_output_line: Bad value for rotation {rotation}")


def _wire_near_line(
    points: list,
    p1: tuple[float | int, float | int],
    p2: tuple[float | int, float | int],
    snapping_range: int,
) -> bool:
    return any(
        _point_to_segment_distance((pt["X"], pt["Y"]), p1, p2) <= snapping_range
        for pt in points
    )


def _point_to_line_distance(
    point: tuple[float | int, float | int],
    p1: tuple[float | int, float | int],
    p2: tuple[float | int, float | int],
) -> float:
    """
    Calculates the distance from a point to an infinite line.

    Args:
        point (tuple[float | int, float | int]): The point to measure from.
        p1 (tuple[float | int, float | int]): One point on the line.
        p2 (tuple[float | int, float | int]): Another point on the line.

    Returns:
        float: The distance from the point to the line.
    """

    x, y = point
    x1, y1 = p1
    x2, y2 = p2

    return (abs((x2 - x1) * (y1 - y) - (x1 - x) * (y2 - y1)) /
        math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))


def _point_to_segment_distance(
    point: tuple[float | int, float | int],
    p1: tuple[float | int, float | int],
    p2: tuple[float | int, float | int],
) -> float:
    """
    Calculates the distance from a point to a line segment.

    Args:
        point (tuple[float | int, float | int]): The point to measure from.
        p1 (tuple[float | int, float | int]): One endpoint of the segment.
        p2 (tuple[float | int, float | int]): The other endpoint of the segment.

    Returns:
        float: The distance from the point to the segment.
    """

    x, y = point
    x1, y1 = p1
    x2, y2 = p2

    dx = x2 - x1
    dy = y2 - y1
    length_sq = dx * dx + dy * dy

    if length_sq == 0:
        return math.hypot(x - x1, y - y1)

    t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / length_sq))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))
