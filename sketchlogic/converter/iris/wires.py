def convert(wires: list) -> None:
    """
    Adds the wires to the output.
    """

    for wire in wires:
        if wire["MainInput"] == {} or wire["MainOutput"] == {}:
            continue

        wire["Points"] = []
