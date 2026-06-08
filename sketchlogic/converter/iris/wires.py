def add(output: list, wires: list) -> list:
    """
    Adds the wires to the output.
    """

    for wire in wires:
        if wire["MainInput"] == {} or wire["MainOutput"] == {}:
            continue

        wire["Points"] = []
        output.append(wire)

    return output
