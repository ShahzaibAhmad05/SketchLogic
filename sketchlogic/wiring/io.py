import numpy
import math
import cv2


def generate(contours: list[numpy.ndarray], wires: list[dict], model_results: list[dict], next_id: int, min_bulkiness: int, snapping_range: int) -> tuple[list, list, int]:
    """
    Generates the toggles and probes based on a cluster test and a proximity test.
    
    Args:
        contours (list[numpy.ndarray]): Contours to generate the toggles and probes from.
        wires (list[dict]): Nearby wires to check for validation.
        model_results (list[dict]): Model results to get the rotation from.
        next_id (int): Next id to use for the toggles and probes.
        min_bulkiness (int): Minimum bulkiness threshold.

    Returns:
        list: The toggles and probes generated.
        list: The wires with the toggles and probes connected.
        int: The next id to use for the circuit objects.
    """

    output = []
    for contour in contours:
        if not _cluster_test(contour) or not _bulkiness_test(contour, min_bulkiness):
            continue

        x, y, w, h = cv2.boundingRect(contour)

        center_x = x + w / 2
        center_y = y + h / 2

        for wire in wires:
            if wire["MainInput"] != {} and wire["MainOutput"] != {}:
                continue
            if wire["MainInput"] == {} and wire["MainOutput"] == {}:
                continue

            point = _get_closest_point(int(center_x), int(center_y), wire["Points"], snapping_range)
            if point is None:
                continue

            io = {
                "$id": str(next_id),
                "CenterX": int(point[0]),
                "CenterY": int(point[1]),
                "Width": 20,
                "Height": 20,
            }
            next_id += 1

            if wire["MainInput"] == {}:
                io["$type"] = "Toggle"
                io["State"] = "Low"
                io["Output"] = {
                    "$id": str(next_id),
                    "Type": "Output"
                }
                wire["MainInput"]["$ref"] = str(next_id)
                next_id += 1

                io["Rotation"] = _get_gate_rotation(wire["MainOutput"]["$ref"], model_results)

            elif wire["MainOutput"] == {}:
                io["$type"] = "Probe"
                io["Input"] = {
                    "$id": str(next_id),
                    "Type": "Input"
                }
                wire["MainOutput"]["$ref"] = str(next_id)
                next_id += 1

                io["Rotation"] = (_get_gate_rotation(wire["MainInput"]["$ref"], model_results) + 180) % 360

            output.append(io)

    return output, wires, next_id


def _cluster_test(contour: numpy.ndarray) -> bool:
    """
    Checks if the contour is a close cluster of points.
    
    Args:
        contour (numpy.ndarray): Contour to check for validation.

    Returns:
        bool: True if the contour is a close cluster of points, False otherwise.
    """

    _, _, w, h = cv2.boundingRect(contour)
    ratio = max(w, h) / min(w, h)

    return ratio < 2.0


def _bulkiness_test(contour: numpy.ndarray, min_bulkiness: float) -> bool:
    """
    Checks if the contour is bulky enough.
    
    Args:
        contour (numpy.ndarray): Contour to check for validation.
        min_bulkiness (float): Minimum bulkiness threshold.

    Returns:
        bool: True if the contour is bulky enough, False otherwise.
    """

    _, _, w, h = cv2.boundingRect(contour)
    return w >= min_bulkiness and h >= min_bulkiness


def _get_closest_point(center_x: int, center_y: int, points: list, tolerance: int) -> tuple[int, int] | None:
    """
    Checks if the contour is close enough to any of the set of points.
    
    Args:
        center_x (int): Center x coordinate of the contour.
        center_y (int): Center y coordinate of the contour.
        points (list): Points to check for validation.
        tolerance (int): Tolerance threshold.

    Returns:
        bool: True if the contour is close enough to any of the set of points, False otherwise.
    """

    closest = min(points, key=lambda p: (center_x - p[0]) ** 2 + (center_y - p[1]) ** 2)
    if math.sqrt((center_x - closest[0]) ** 2 + (center_y - closest[1]) ** 2) <= tolerance:
        return closest

    return None


def _get_gate_rotation(ref: str, gates: list[dict]) -> int:
    """
    Gets the rotation of a gate based on the given reference id.
    
    Args:
        ref (str): The reference id of the gate.

    Returns:
        int: The rotation of the gate.
    """

    for gate in gates:
        if gate["Output"]["$id"] == ref:
            return gate["Rotation"]

        if gate["$type"] == "NotGate" and gate["Input"]["$id"] == ref:
            return gate["Rotation"]
        else:
            for input in gate["Inputs"]:
                if input["$id"] == ref:
                    return gate["Rotation"]

    return 0
