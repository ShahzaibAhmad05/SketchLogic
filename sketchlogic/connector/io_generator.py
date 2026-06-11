import numpy
import math
import cv2


def generate(wires: list, model_results: list, next_id: int, debug: bool) -> tuple[list, int]:
    """
    Generates the toggles and probes wherever the wires are disconnected.

    Args:
        wires (list): Wires to generate the toggles and probes for.
        model_results (list): Model results to compare endpoints with
        next_id (int): Next id to use for the toggles and probes.
        debug (bool): Whether to print debug information.

    Returns:
        int: The next id to use for the circuit objects.
    """

    output = []
    toggles_generated = 0
    probes_generated = 0

    for wire in wires:
        points = wire["Points"]
        mainInput = wire["MainInput"]
        mainOutput = wire["MainOutput"]

        if (mainInput == {} and mainOutput == {}) or (mainInput != {} and mainOutput != {}):
            continue

        if mainInput != {}:
            ref_comp = _get_co_with_pin_ref(mainInput["$ref"], model_results)
        elif mainOutput != {}:
            ref_comp = _get_co_with_pin_ref(mainOutput["$ref"], model_results)
        else:
            continue

        cx, cy = ref_comp["CenterX"], ref_comp["CenterY"]
        w, h = ref_comp["Width"], ref_comp["Height"]
        rotation = ref_comp["Rotation"]
        comp_type = ref_comp["$type"]

        if comp_type == "NotGate":
            num_inputs = 1
        elif comp_type.endswith("Gate") and comp_type != "NotGate":
            num_inputs = len(ref_comp["Inputs"])
        else:
            continue

        end1 = points[0]
        end2 = points[-1]

        valid_point = (
            end1 if _point_to_point_distance(end1, (cx, cy)) > _point_to_point_distance(end2, (cx, cy)) 
            else end2
        )

        io = {
            "$id": str(next_id),
            "CenterX": int(valid_point[0]),
            "CenterY": int(valid_point[1]),
            "Width": w / max(3, num_inputs),
            "Height": h / max(3, num_inputs),
            "Rotation": rotation,
        }
        next_id += 1

        if mainInput == {}:
            io["$type"] = "Toggle"
            io["State"] = "Low"
            io["Output"] = {
                "$id": str(next_id),
                "Type": "Output"
            }
            mainInput["$ref"] = str(next_id)
            next_id += 1
            toggles_generated += 1

        elif mainOutput == {}:
            io["$type"] = "Probe"
            io["Input"] = {
                "$id": str(next_id),
                "Type": "Input"
            }
            mainOutput["$ref"] = str(next_id)
            next_id += 1
            probes_generated += 1

        output.append(io)

    if debug:
        print()
        print(f"sketchlogic.connector.io_generator:")
        print(f"Toggles generated: {toggles_generated}")
        print(f"Probes generated: {probes_generated}")
    
    return output, next_id


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


def _get_co_with_pin_ref(pin_ref: str, circuit_objects: list) -> dict:
    """
    Gets the circuit object with the given pin reference id.
    """

    for co in circuit_objects:
        if co["$type"] == "Wire":
            if co["MainInput"]["$ref"] == pin_ref or co["MainOutput"]["$ref"] == pin_ref:
                return co

        if co["$type"] in ["NotGate", "Probe"]:
            if co["Input"]["$id"] == pin_ref:
                return co

        if co["$type"].endswith("Gate") and co["$type"] != "NotGate":
            for input in co["Inputs"]:
                if input["$id"] == pin_ref:
                    return co

        if co["$type"].endswith("Gate") or co["$type"] == "Toggle":
            if co["Output"]["$id"] == pin_ref:
                return co

    return {}
