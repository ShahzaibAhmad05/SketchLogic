def convert(results: list[dict]) -> list[dict]:
    """
    Converts the given results to a simulatable circuit json format.
    
    Args:
        results (list[dict]): The results to convert.

    Returns:
        list[dict]: The converted results.
    """

    output = []
    for result in results:
        output.append({
            "$id": result["id"],
            "$type": result["type"],
            "CenterX": result["centerX"],
            "centerY": result["centerY"],
            "Inputs": result["inputs"],
            "Output": result["output"],
            "Rotation": result["rotation"]
        })

    return output
