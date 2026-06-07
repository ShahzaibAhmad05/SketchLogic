from typing import Any
import math


def convert_to_serializable_dict(results: list) -> list[dict]:
    """
    Converts the given results to a serializable dictionary.

    Args:
        results (list): The results to convert.

    Returns:
        list[dict]: The converted results.
    """
    i = 1
    output = []

    for result in results:
        class_name = class_to_name(result["Class"])
        rotation = class_to_rotation(result["Class"])

        output.append({
            "$id": str(i),
            "$type": class_name,
            "CenterX": result["CenterX"],
            "CenterY": result["CenterY"],
            "Width": result["Width"],
            "Height": result["Height"],
            "Rotation": rotation
        })

        i += 1

    return output


def class_to_name(class_id: int) -> str:
    """
    Converts a class ID to a class name for the inference results. This should be consistent with the YAML config file in the dataset that the model was trained with.

    Args:
        class_id (int): The class ID

    Returns:
        str: The class name
    """

    return {
        0: "AndGate",
        1: "OrGate",
        2: "NotGate",
        3: "NandGate",
        4: "NorGate",
        5: "XorGate",
        6: "XnorGate",
    }[class_id // 4]


def class_to_rotation(class_id: int) -> int:
    """
    Converts a class ID to a rotation angle for the inference results.

    Args:
        class_id (int): The class ID

    Returns:
        int: The rotation angle
    """

    return round(class_id % 4) * 90
