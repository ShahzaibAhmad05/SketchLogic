import math


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
    num_output_connections = 0
    num_input_connections = 0

    for component in model_results:
        comp_type = component["$type"]
        cx, cy = component["CenterX"], component["CenterY"]
        w, h = component["Width"], component["Height"]

        if not comp_type.endswith("Gate"):
            continue

        for side in ["left", "right"]:      # corresponds to input, output
            s1, s2 = _get_side(side, int(cx), int(cy), int(w), int(h), component["Rotation"])

            nearby_wires = _get_nearby_wires(wires, s1, s2, max_range)
            min_num_pins = 1 if side == "right" else 2
            num_pins_to_add = max(min_num_pins, len(nearby_wires))

            pin_positions = _divide_segment(s1, s2, num_pins_to_add)
            if comp_type != "NotGate" and side == "left":
                next_id = _add_input_pins(component, num_pins_to_add, next_id)

            for wire in nearby_wires:
                pin_idx = _find_closest_pin_index(wire, pin_positions, debug)
                
                if side == "right" and wire["MainInput"] == {}:
                    wire["MainInput"]["$ref"] = component["Output"]["$id"]
                    num_output_connections += 1

                elif side == "left" and wire["MainOutput"] == {}:
                    if comp_type == "NotGate":
                        wire["MainOutput"]["$ref"] = component["Input"]["$id"]
                    else:
                        wire["MainOutput"]["$ref"] = component["Inputs"][pin_idx]["$id"]
                    num_input_connections += 1

    # MARK AND SWEEP PHASE BEFORE LEAVING
    wires_to_remove = []
    for wire in wires:
        if wire["MainInput"] == {} and wire["MainOutput"] == {}:
            wires_to_remove.append(wire)
    for wire in wires_to_remove:
        wires.remove(wire)

    if debug:
        print()
        print(f"sketchlogic.connector.wiring.connector:")
        print(f"{total_wires * 2} connections attempted.")
        print(f"component output connections formed: {num_output_connections}")
        print(f"component input connections formed: {num_input_connections}")

        if len(wires_to_remove) > 0:
            print(f"{len(wires_to_remove)} wires had to be removed.")
            print(f"please avoid passing disconnected wires here.")

    return next_id


def _add_input_pins(component: dict, num_pins: int, next_id: int) -> int:
    """
    Adds the given number of input pins to the component.
    
    Args:
        component (dict): The component to add the pins to.
        num_pins (int): The number of pins to add.
        next_id (int): The next id to use for the pins.

    Returns:
        int: The next id to use for the pins.
    """

    for _ in range(num_pins):
        component["Inputs"].append({
            "$id": str(next_id),
            "Type": "Input"
        })
        next_id += 1

    return next_id


def _find_closest_pin_index(
    wire: dict,
    pin_positions: list[tuple[float, float]],
    debug: bool,
    starting_range: float = 40.0,
    range_multiplier: float = 1.25,
    patience: int = 3,
    max_iterations: int = 30,
) -> int:
    """
    Finds the closest pin to the given wire. 
    
    Args:
        wire (dict): The wire to check.
        pin_positions (list[tuple[float, float]]): The positions of the pins to check.
        debug (bool): Whether to print debug information.
        starting_range (float): The starting range to look for the closest pin.
        range_multiplier (float): The multiplier to use for the range.
        patience (int): The number of times to try to find the closest pin before raising an error.
        max_iterations (int): The maximum number of iterations to try to find the closest pin.

    Returns:
        int: The index of the closest pin.
    """

    closest_distance = float('inf')
    closest_pin_index = None
    iteration = 1

    while closest_pin_index is None:
        if iteration == max_iterations and debug:
            print()
            print("sketchlogic.connector.wiring.connector:")
            print(f"Failed to find closest pin after {max_iterations} iterations.")
            exit(1)

        for pin_position in pin_positions:
            points = wire["Points"]
            idx = pin_positions.index(pin_position)

            for point in points:
                dist = _point_to_point_distance(point, pin_position)
                if dist <= starting_range and dist < closest_distance:
                    closest_distance = dist
                    closest_pin_index = idx

        starting_range = starting_range * range_multiplier
        iteration += 1

    if iteration > patience and debug:
        print()
        print("sketchlogic.connector.wiring.connector:")
        print(f"warning: iteration {iteration} reached.")
        print(f"consider increasing starting range or range multiplier.")

    return closest_pin_index


def _get_side(
    side: str, cx: int, cy: int, w: int, h: int, rotation: int
) -> tuple[tuple[float, float], tuple[float, float]]:
    """
    Gets the side of a gate represented by two points

    Args:
        side (str): Choose from ["left", "right", "top", "bottom"].
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
        3: ((x, y + h), (x + w, y + h))     # bottom
    }

    shift = rotation // 90
    return mapping[(side_mapping[side.lower()] + shift) % 4]


def _divide_segment(p1: tuple[float, float], p2: tuple[float, float], divider: int) -> list[tuple[float, float]]:
    """
    Divides a segment into a list of points. This was put in by Claude but it works.
    
    Args:
        p1 (tuple[float, float]): One endpoint of the segment.
        p2 (tuple[float, float]): The other endpoint of the segment.
        divider (int): The number of points to divide the segment into.

    Returns:
        list[tuple[float, float]]: The points that divide the segment.
    """

    if divider == 0: return []
    dx = (p2[0] - p1[0]) / divider
    dy = (p2[1] - p1[1]) / divider

    return [
        (p1[0] + dx * (i + 0.5), p1[1] + dy * (i + 0.5))
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
