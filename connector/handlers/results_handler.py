import json
from pathlib import Path


def load_model_results(model_results_json_path: Path) -> list[dict]:
    """
    Gets the results from the model results JSON file.

    Args:
        model_results_json_path (Path): Path to the model results JSON file

    Returns:
        list: A list of dictionaries containing the model results
    """

    with open(model_results_json_path, "r") as file:
        return json.load(file)


def remove_entries(results: list[dict], entries: list[str]) -> None:
    """
    Removes the entries from the model results.

    Args:
        results (list[dict]): The model results
        entries (list[str]): The entries to remove
    """

    for result in results:
        for entry in entries:
            del result[entry]
