import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """
    Parses the arguments for the model module.
    """

    parser = argparse.ArgumentParser(
        prog="model",
        description="Run inference on an image and write results to JSON.",
    )

    parser.add_argument(
        "input_image_path",
        type=_existing_path,
        help="path to the input image",
    )

    parser.add_argument(
        "output_json_path",
        type=Path,
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
