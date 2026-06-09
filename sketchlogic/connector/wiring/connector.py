import math
from typing import Literal


def connect(wires: list, model_results: list, next_id: int, max_range: int, debug: bool = False) -> int:
    """
    Connects the wires with the model results.

    Args:
        wires (list): The original list of wires to connect.
        model_results (list): The original list of model results to connect the wires to.
        next_id (int): The next id to use for the wires.
        max_range (int): Max range to look for when doing wire snapping.
        debug (bool): Whether to print debug information.

    Returns:
        tuple[list, list, int]: A tuple containing the connected wires, the model results, and the next id.
    """

    total_wires = len(wires)
    total_results = len(model_results)

    for result in model_results:
        if not result["$type"].endswith("Gate"):
            continue

        gate = result
        cx, cy, w, h = gate["CenterX"], gate["CenterY"], gate["Width"], gate["Height"]

        i1, i2 = _get_side("left", int(cx), int(cy), int(w), int(h), gate["Rotation"])
        nearby_input_wires = _get_nearby_wires(wires, i1, i2, max_range)
        if len(nearby_input_wires) == 0:
            continue

        input_pins = _divide_segment(i1, i2, len(nearby_input_wires))
        for pin in input_pins:
            closest_distance = float('inf')
            closest_wire = nearby_input_wires[0]

            for wire in nearby_input_wires:
                if wire["MainOutput"] != {}:
                    continue
                
                for point in wire["Points"]:
                    dist = _point_to_point_distance(pin, point)

                    if dist < closest_distance:
                        closest_distance = dist
                        closest_wire = wire

            if gate["$type"] == "NotGate":
                closest_wire["MainOutput"]["$ref"] = gate["Input"]["$id"]
            else:
                gate["Inputs"].append({
                    "$id": str(next_id),
                    "Type": "Input"
                })
                closest_wire["MainOutput"]["$ref"] = str(next_id)
                next_id += 1

    for result in model_results:
        if not result["$type"].endswith("Gate"):
            continue

        gate = result
        cx, cy, w, h = gate["CenterX"], gate["CenterY"], gate["Width"], gate["Height"]

        o1, o2 = _get_side("right", int(cx), int(cy), int(w), int(h), gate["Rotation"])
        nearby_output_wires = _get_nearby_wires(wires, o1, o2, max_range)
        if len(nearby_output_wires) != 1:
            continue

        output_pins = _divide_segment(o1, o2, len(nearby_output_wires))
        pin = output_pins[0]

        nearby_output_wire = nearby_output_wires[0]
        if nearby_output_wire["MainInput"] != {}:
            continue

        nearby_output_wire["MainInput"]["$ref"] = gate["Output"]["$id"]

    # MARK AND SWEEP PHASE BEFORE LEAVING

    wires_to_remove = []
    results_to_remove = []

    for wire in wires:
        if wire["MainInput"] == {} and wire["MainOutput"] == {}:
            wires_to_remove.append(wire)

    for gate in model_results:
        if gate["$type"] != "NotGate" and len(gate["Inputs"]) < 2:
            results_to_remove.append(gate)

    for wire in wires_to_remove:
        wires.remove(wire)

    for gate in results_to_remove:
        model_results.remove(gate)

    if debug:
        print()
        print(f"sketchlogic.connector.wiring.connector:")
        print(f"{total_wires} wires attempted to connect to {total_results} components")
        print(f"components connected: {total_results - len(results_to_remove)}")
        print(f"wires connected: {total_wires - len(wires_to_remove)}")

    return next_id


def _get_side(
    side: Literal["left", "top", "right", "bottom"], 
    cx: int, cy: int, w: int, h: int, rotation: int
) -> tuple[tuple[float, float], tuple[float, float]]:
    """
    Gets the side of a gate represented by two points

    Args:
        side (Literal["left", "top", "right", "bottom"]): The side to get.
        cx (int): The x coordinate of the center of the gate.
        cy (int): The y coordinate of the center of the gate.
        w (int): The width of the gate.
        h (int): The height of the gate.
        rotation (int): The rotation of the gate.

    Returns:
        tuple[tuple[int, int], tuple[int, int]]: A tuple of two points that represent the side of the gate.
    """

    side_mapping = {"left": 0, "top": 1, "right": 2, "bottom": 3}
    x = cx - w / 2
    y = cy - h / 2

    mapping = {
        0: ((x, y), (x, y + h)),            # left
        1: ((x, y), (x + w, y)),            # top
        2: ((x + w, y), (x + w, y + h)),    # right
        3: ((x, y + h), (x + h, y + h))     # bottom
    }

    shift = rotation // 90
    return mapping[(side_mapping[side.lower()] + shift) % 4]


def _divide_segment(p1: tuple[float, float], p2: tuple[float, float], divider: int) -> list[tuple[float, float]]:
    """
    Divides a segment into a list of points.
    
    Args:
        p1 (tuple[float, float]): One endpoint of the segment.
        p2 (tuple[float, float]): The other endpoint of the segment.
        divider (int): The number of points to divide the segment into.

    Returns:
        list[tuple[float, float]]: The points that divide the segment.
    """

    return [
        (p1[0] + (p2[0] - p1[0]) * (i + 0.5) / divider, p1[1] + (p2[1] - p1[1]) * (i + 0.5) / divider) 
        for i in range(divider)
    ]


def _get_nearby_wires(wires: list, p1: tuple[float, float], p2: tuple[float, float], max_range: int) -> list:
    """
    Gets the wires that are near the given side represented by two points.
    
    Args:
        wires (list): The wires to check.
        p1 (tuple[float, float]): One endpoint of the side.
        p2 (tuple[float, float]): The other endpoint of the side.
        max_range (int): The maximum range to look for.

    Returns:
        list: The wires that are near the given side.
    """

    return [
        wire for wire in wires if any(
            _point_to_segment_distance(points, p1, p2) <= max_range for points in wire["Points"]
        )
    ]
    

def _point_to_segment_distance(
    point: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float]
) -> float:
    """
    Calculates the distance from a point to a line segment.

    Args:
        point (tuple[float, float]): The point to measure from.
        p1 (tuple[float, float]): One endpoint of the segment.
        p2 (tuple[float, float]): The other endpoint of the segment.

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


def _point_to_point_distance(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """
    Calculates the distance from a point to a point.
    
    Args:
        p1 (tuple[float, float]): The first point.
        p2 (tuple[float, float]): The second point.

    Returns:
        float: The distance from the first point to the second point.
    """

    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])
