def calculate(components: list, per_component: int) -> float:
    """
    Calculates the scale factor based on the model results.
    """

    min_x, min_y = _get_min_point(components)
    max_x, max_y = _get_max_point(components)

    required_max_side = len(components) * per_component
    current_max_side = max(max_x - min_x, max_y - min_y)
    
    return required_max_side / current_max_side


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
