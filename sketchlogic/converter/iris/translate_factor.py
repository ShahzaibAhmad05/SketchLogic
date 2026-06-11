def calculate(model_results: list, scale_factor: float, center_x: float, center_y: float) -> tuple[float, float]:
    """
    Calculates the translate factor based on the model results.
    """

    min_x, min_y = _get_min_point(model_results)
    max_x, max_y = _get_max_point(model_results)

    average_x = ((max_x + min_x) / 2) * scale_factor
    average_y = ((max_y + min_y) / 2) * scale_factor

    return center_x - average_x, center_y - average_y


def _get_max_point(model_results: list) -> tuple[float, float]:
    """
    Gets the maximum point from the model results.
    """

    max_x = float('-inf')
    max_y = float('-inf')

    for component in model_results:
        max_x = max(max_x, component["CenterX"] + (component["Width"] / 2))
        max_y = max(max_y, component["CenterY"] + (component["Height"] / 2))

    return max_x, max_y


def _get_min_point(model_results: list) -> tuple[float, float]:
    """
    Gets the minimum point from the model results.
    """

    min_x = float('inf')
    min_y = float('inf')

    for component in model_results:
        min_x = min(min_x, component["CenterX"] - (component["Width"] / 2))
        min_y = min(min_y, component["CenterY"] - (component["Height"] / 2))

    return min_x, min_y
