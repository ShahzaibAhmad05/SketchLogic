def remove_entries_from_gates(results: list[dict], entries: list[str]) -> list[dict]:
    """
    Removes the entries from the model results.
    """

    for result in results:
        if (result["$type"].endswith("Gate")):
            for entry in entries:
                del result[entry]

    return results


def clear_wire_points(results: list[dict]) -> list[dict]:
    """
    Removes the points from the wires.
    """

    for result in results:
        if (result["$type"] == "Wire"):
            result["Points"] = []

    return results
