import math


def straighten(model_results: list, io_results: list, wires: list, space_factor: int, debug: bool) -> None:
    """
    Straightens the models and io if they have a 2 point wire in-between.
    """

    straightened_counts = []
    for component in model_results:
        straightened_count = refresh_component_pins(
            component, [], 
            wires, model_results, io_results, 
            space_factor
        )
        straightened_counts.append(straightened_count)

    if debug:
        print()
        print(f"sketchlogic.converter.iris.straightener:")
        print(f"Straightened {sum(straightened_counts)} connections.")


def refresh_component_pins(
    component: dict, fixed_pins: list, 
    wires: list, components: list, io: list, 
    space_factor: int, straightened_count: int = 0
) -> int:
    """
    Refreshes the component attachments and their attachments recursively. Assumes the input 
    components and io to have CenterX and CenterY and Height and Width.

    Args:
        component: The component to refresh the attachments of.
        fixed_pins: The references of pins that are already fixed.
        wires: The wires in the circuit.
        components: The components in the circuit.
        io: The io in the circuit.
        space_factor: The minimum length to ensure for dual-point wires.
    """

    self_pin_refs = _get_component_pin_refs(component, blacklist=fixed_pins)
    if not self_pin_refs: return straightened_count

    attached_wires = []
    attached_pin_refs = []
    attached_ios = []

    for self_pin_ref in self_pin_refs:
        attached_wire = _get_co_with_pin_ref(self_pin_ref, wires)
        attached_wires.append(attached_wire)

        if attached_wire is None:
            attached_pin_refs.append(None)
            attached_ios.append(None)
            continue

        if attached_wire["MainInput"]["$ref"] == self_pin_ref:
            attached_pin_refs.append(attached_wire["MainOutput"]["$ref"])
            attached_ios.append(_get_co_with_pin_ref(attached_wire["MainOutput"]["$ref"], io))
        else:
            attached_pin_refs.append(attached_wire["MainInput"]["$ref"])
            attached_ios.append(_get_co_with_pin_ref(attached_wire["MainInput"]["$ref"], io))

    for attached_wire in attached_wires:
        if attached_wire is None or len(attached_wire["Points"]) != 2:
            continue

        idx = attached_wires.index(attached_wire)
        self_pin_ref = self_pin_refs[idx]
        attached_pin_ref = attached_pin_refs[idx]
        attached_io = attached_ios[idx]

        p1 = attached_wire["Points"][0]
        p2 = attached_wire["Points"][1]

        if _point_to_point_distance(p1, p2) >= space_factor:
            continue
        else:
            straightened_count += 1

        x_diff = abs(p1[0] - p2[0])
        y_diff = abs(p1[1] - p2[1])

        is_vertical = x_diff < y_diff
        if attached_io and attached_io["$type"] in ["Toggle", "Probe"]:
            if component["$type"] == "NotGate":
                if is_vertical:
                    attached_io["CenterX"] = component["CenterX"]
                    if component["Y"] - attached_io["Y"] > 0:
                        attached_io["CenterY"] = component["CenterY"] - 30 - space_factor - 20
                    else:
                        attached_io["CenterY"] = component["CenterY"] + 30 + space_factor + 20

                else:
                    attached_io["CenterY"] = component["CenterY"]
                    if component["CenterX"] - attached_io["CenterX"] > 0:
                        attached_io["CenterX"] = component["CenterX"] - 30 - space_factor - 20
                    else:
                        attached_io["CenterX"] = component["CenterX"] + 30 + space_factor + 20

            else:
                num_inputs = len(component["Inputs"])

                pin_idx_relative = (num_inputs - 1) / 2
                for input in component["Inputs"]:
                    if input["$id"] == self_pin_ref:
                        pin_idx_relative = component["Inputs"].index(input)

                comp_y = component["CenterY"] - (component["Height"] / 2)
                comp_x = component["CenterX"] - (component["Width"] / 2)

                if is_vertical:
                    attached_io["CenterX"] = comp_x + (20 * pin_idx_relative) + 10
                    if component["CenterY"] - attached_io["CenterY"] > 0:
                        attached_io["CenterY"] = comp_y - 40 - space_factor + 10
                    else:
                        attached_io["CenterY"] = comp_y + 20 + (num_inputs * 20) + space_factor + 10

                else:
                    attached_io["CenterY"] = comp_y + (20 * pin_idx_relative) + 10
                    if component["CenterX"] - attached_io["CenterX"] > 0:
                        attached_io["CenterX"] = comp_x - 40 - space_factor + 10
                    else:
                        attached_io["CenterX"] = comp_x + 20 + (num_inputs * 20) + space_factor + 10

        else:
            attached_component = _get_co_with_pin_ref(attached_pin_ref, components)
            if attached_component:
                if (component["$type"] == "NotGate" or 
                    (component["$type"].endswith("Gate") and len(component["Inputs"]) == 2)):
                    if is_vertical:
                        attached_component["CenterX"] = component["CenterX"]
                        if component["CenterY"] - attached_component["CenterY"] > 0:
                            attached_component["CenterY"] = component["CenterY"] - 10 - space_factor
                        else:
                            attached_component["CenterY"] = component["CenterY"] + 50 + space_factor

                    else:
                        attached_component["CenterY"] = component["CenterY"]
                        if component["CenterX"] - attached_component["CenterX"] > 0:
                            attached_component["CenterX"] = component["CenterX"] - 60 - space_factor
                        else:
                            attached_component["CenterX"] = component["CenterX"] + 60 + space_factor

                fixed_pins.append(attached_pin_ref)
                refresh_component_pins(
                    attached_component, fixed_pins, wires,
                    components, io, space_factor, 
                    straightened_count=straightened_count
                )

    return straightened_count


def _get_component_pin_refs(component: dict, blacklist: list) -> list:
    """
    Gets the pin references of the component. Currently supports only gates.
    """

    comp_type = component["$type"]
    self_pin_refs = []

    if comp_type == "NotGate":
        if component["Input"]["$id"] not in blacklist:
            self_pin_refs.append(component["Input"]["$id"])

        if component["Output"]["$id"] not in blacklist:
            self_pin_refs.append(component["Output"]["$id"])

    elif comp_type.endswith("Gate") and comp_type != "NotGate":
        for input in component["Inputs"]:
            if input["$id"] not in blacklist: 
                self_pin_refs.append(input["$id"])

        if component["Output"]["$id"] not in blacklist:
            self_pin_refs.append(component["Output"]["$id"])
    else:
        return []

    return self_pin_refs


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



def get_pin_with_ref(pin_ref: str, circuit_objects: list) -> dict:
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
