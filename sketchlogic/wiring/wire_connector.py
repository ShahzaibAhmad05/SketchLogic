import math


def connect(wires: list, model_results: list, next_id: int, snapping_range: int) -> tuple[list, list, int]:
    """
    Connects the wires with the model results.
    
    Args:
        wires (list): The wires to connect.
        model_results (list): The model results to connect the wires to.
        next_id (int): The next id to use for the wires.
        snapping_range (int): The snapping range to use for the wires.

    Returns:
        list: The connected json objects.
        int: The next id to use for the wires.
    """

    for gate in model_results:
        cx, cy, w, h = gate["CenterX"], gate["CenterY"], gate["Width"], gate["Height"]

        i1, i2 = _get_side(0, int(cx), int(cy), int(w), int(h), gate["Rotation"])
        o1, o2 = _get_side(2, int(cx), int(cy), int(w), int(h), gate["Rotation"])

        input_side_complete = False
        output_side_complete = False

        for wire in wires:
            if wire["MainInput"] != {} and wire["MainOutput"] != {}:
                continue

            if gate["$type"] == "NotGate":
                snapped = False

                if not input_side_complete and wire["MainOutput"] == {}:
                    if _wire_near_side(wire["Points"], i1, i2, snapping_range):
                        snapped = True
                        wire["MainOutput"]["$ref"] = gate["Input"]["$id"]
                        input_side_complete = True

                if not snapped and not output_side_complete and wire["MainInput"] == {}:
                    if _wire_near_side(wire["Points"], o1, o2, snapping_range):
                        wire["MainInput"]["$ref"] = gate["Output"]["$id"]
                        output_side_complete = True

            else:
                snapped = False

                if not output_side_complete and wire["MainInput"] == {}:
                    if _wire_near_side(wire["Points"], o1, o2, snapping_range):
                        snapped = True
                        wire["MainInput"]["$ref"] = gate["Output"]["$id"]
                        output_side_complete = True

                if not snapped and wire["MainOutput"] == {}:
                    if _wire_near_side(wire["Points"], i1, i2, snapping_range):
                        wire["MainOutput"]["$ref"] = str(next_id)

                        gate["Inputs"].append({
                            "$id": str(next_id),
                            "Type": "Input"
                        })
                        next_id += 1

    return wires, model_results, next_id


def _get_side(side: int, center_x: int, center_y: int, width: int, height: int, rotation: int) -> tuple:
    """
    Gets the side of a gate. side variable is an int according to:
        0=left, 1=top, 2=right, 3=bottom

    Args:
        side (int): The side of the gate.
        center_x (int): The x coordinate of the center of the gate.
        center_y (int): The y coordinate of the center of the gate.
        width (int): The width of the gate.
        height (int): The height of the gate.
        rotation (int): The rotation of the gate.

    Returns:
        tuple: A tuple of two points that represent the left side of the gate.
    """

    x = center_x - width / 2
    y = center_y - height / 2

    mapping = {
        0: ((x, y), (x, y + height)),                       # left
        1: ((x, y), (x + width, y)),                        # top
        2: ((x + width, y), (x + width, y + height)),       # right
        3: ((x, y + height), (x + width, y + height))       # bottom
    }

    shift = rotation // 90
    return mapping[(side + shift) % 4]


def _wire_near_side(points: list, p1: tuple[int, int], p2: tuple[int, int], distance: int) -> bool:
    """
    Checks if the wire is near the side of the gate.
    
    Args:
        points (list): The points of the wire.
        p1 (tuple[int, int]): One endpoint of the side.
        p2 (tuple[int, int]): The other endpoint of the side.
    """

    return any(
        _point_to_segment_distance(point, p1, p2) < distance
        for point in points
    )
    

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
