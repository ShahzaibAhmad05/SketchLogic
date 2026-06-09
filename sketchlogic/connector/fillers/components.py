def fill_toggle_probes(results: list[dict], next_id: int) -> tuple[list, int]:
    """
    Fills the toggle probes in the results.

    Args:
        results (list[dict]): The results to fill the toggle probes in.
        next_id (int): The next id to use for the toggle probes.

    Returns:
        tuple: A tuple of the results with the toggle probes filled and the next id.
        int: The next id to use for the toggle probes.
    """

    for result in results:
        if result["$type"] == "Wire":
            if result["MainInput"] == {}:
                
                pass

    return results, next_id


def _create_toggle(points: list, next_id: int) -> tuple[dict, int]:
    """
    Creates a toggle switch.
    
    Args:
        points (list): The points of the toggle switch.
        next_id (int): The next id to use for the toggle switch.

    Returns:
        tuple: A tuple of the toggle switch and the next id.
    """


    return {
        "$id": str(next_id),
        "$type": "Toggle",
        "State": "Low",
        "Output": {
            "$id": str(next_id + 1),
            "Type": "Output"
        },
        "CenterX": 0,
        "CenterY": 0,
        "Rotation": 0
    }, next_id + 2
