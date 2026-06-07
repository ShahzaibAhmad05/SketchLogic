import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """
    Parses the arguments for the connector module.
    """

    parser = argparse.ArgumentParser(
        prog="connector",
        description="Connect circuit gates based on model results and write output to JSON.",
    )

    parser.add_argument(
        "input_image_path",
        type=_existing_path,
        help="path to the input image",
    )

    parser.add_argument(
        "model_results_json_path",
        type=_existing_file,
        help="path to the model results JSON file",
    )

    parser.add_argument(
        "output_json_path",
        type=_existing_file,
        help="path to the output JSON file",
    )

    return parser.parse_args()


def _existing_path(path_str: str):
    """
    Type function that ensures it has an existing path.
    """

    path = Path(path_str)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"Path does not exist: {path}")

    return path


def _existing_file(path_str: str):
    """
    Type function that ensures it has an existing file.
    """

    path = Path(path_str)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"Path is not a file: {path}")

    return path
