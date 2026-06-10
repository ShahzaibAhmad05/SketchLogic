def straighten(model_results: list, io_results: list, wires: list, space_factor: int) -> None:
    """
    Straightens the models and io if they have a 2 point wire in-between.
    """

    for component in model_results:
        refresh_component_pins(component, [], wires, model_results, io_results, space_factor)


def refresh_component_pins(component: dict, fixed_pins: list, wires: list, components: list, io: list, space_factor: int) -> None:
    """
    Refreshes the component attachments and their attachments recursively.

    Args:
        component: The component to refresh the attachments of.
        fixed_pins: The references of pins that are already fixed.
        wires: The wires in the circuit.
        components: The components in the circuit.
        io: The io in the circuit.
        space_factor: The space factor to use for the new pins.

    Returns:
        None
    """

    if component["$type"].endswith("Gate"):
        self_pin_refs = []
        attached_wires = []
        attached_pin_refs = []
        attached_ios = []

        if component["$type"] == "NotGate":
            if component["Input"]["$id"] not in fixed_pins:
                self_pin_refs.append(component["Input"]["$id"])
        else:
            for input in component["Inputs"]:
                if input["$id"] not in fixed_pins: 
                    self_pin_refs.append(input["$id"])

        if component["Output"]["$id"] not in fixed_pins:
            self_pin_refs.append(component["Output"]["$id"])

        for self_pin_ref in self_pin_refs:
            attached_wire = _get_co_with_pin_ref(self_pin_ref, wires)
            attached_wires.append(attached_wire)

            if attached_wire["MainInput"]["$ref"] == self_pin_ref:
                attached_pin_refs.append(attached_wire["MainOutput"]["$ref"])
                attached_ios.append(_get_co_with_pin_ref(attached_wire["MainOutput"]["$ref"], io))
            else:
                attached_pin_refs.append(attached_wire["MainInput"]["$ref"])
                attached_ios.append(_get_co_with_pin_ref(attached_wire["MainInput"]["$ref"], io))

        for attached_wire in attached_wires:
            idx = attached_wires.index(attached_wire)
            self_pin_ref = self_pin_refs[idx]
            attached_pin_ref = attached_pin_refs[idx]
            attached_io = attached_ios[idx]

            if attached_wire and attached_wire["$type"] == "Wire":
                p1 = attached_wire["Points"][0]
                p2 = attached_wire["Points"][1]

                x_diff = abs(p1[0] - p2[0])
                y_diff = abs(p1[1] - p2[1])

                if x_diff == space_factor or y_diff == space_factor:
                    continue

                is_vertical = x_diff < y_diff
                if attached_io and attached_io["$type"] in ["Toggle", "Probe"]:
                    if component["$type"] == "NotGate":
                        if is_vertical:
                            attached_io["X"] = component["X"] + 10
                            if component["Y"] - attached_io["Y"] > 0:
                                attached_io["Y"] = component["Y"] - 40 - space_factor
                            else:
                                attached_io["Y"] = component["Y"] + 60 + space_factor

                        else:
                            attached_io["Y"] = component["Y"] + 10
                            if component["X"] - attached_io["X"] > 0:
                                attached_io["X"] = component["X"] - 40 - space_factor
                            else:
                                attached_io["X"] = component["X"] + 60 + space_factor

                    else:
                        num_inputs = len(component["Inputs"])

                        pin_idx_relative = (num_inputs - 1) / 2
                        for input in component["Inputs"]:
                            if input["$id"] == self_pin_ref:
                                pin_idx_relative = component["Inputs"].index(input)

                        if is_vertical:
                            attached_io["X"] = component["X"] + (20 * pin_idx_relative)
                            if component["Y"] - attached_io["Y"] > 0:
                                attached_io["Y"] = component["Y"] - 40 - space_factor
                            else:
                                attached_io["Y"] = component["Y"] + 20 + (num_inputs * 20) + space_factor

                        else:
                            attached_io["Y"] = component["Y"] + (20 * pin_idx_relative)
                            if component["X"] - attached_io["X"] > 0:
                                attached_io["X"] = component["X"] - 40 - space_factor
                            else:
                                attached_io["X"] = component["X"] + 20 + (num_inputs * 20) + space_factor

                else:
                    attached_component = _get_co_with_pin_ref(attached_pin_ref, components)
                    if attached_component:
                        if (component["$type"] == "NotGate" or 
                            (component["$type"].endswith("Gate") and len(component["Inputs"]) == 2)):
                            if is_vertical:
                                attached_component["X"] = component["X"]
                                if component["Y"] - attached_component["Y"] > 0:
                                    attached_component["Y"] = component["Y"] - 10 - space_factor
                                else:
                                    attached_component["Y"] = component["Y"] + 50 + space_factor

                            else:
                                attached_component["Y"] = component["Y"]
                                if component["X"] - attached_component["X"] > 0:
                                    attached_component["X"] = component["X"] - 60 - space_factor
                                else:
                                    attached_component["X"] = component["X"] + 60 + space_factor

                        fixed_pins.append(attached_pin_ref)
                        refresh_component_pins(
                            attached_component, fixed_pins, wires,
                            components, io, space_factor
                        )


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
