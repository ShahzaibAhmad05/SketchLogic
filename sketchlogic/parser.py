import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """
    Parses the arguments for the sketchlogic system.
    """

    parser = argparse.ArgumentParser(
        prog="sketchlogic",
        description="Convert an image to a simulation.",
    )

    parser.add_argument(
        "input_image_path",
        type=_existing_path,
        help="path to the input image",
    )

    parser.add_argument(
        "output_json_path",
        type=_file_path,
        help="path to write the output file to",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="enable debugging (outputs test files and prints logs)",
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


def _file_path(path_str: str):
    """
    Type function that ensures it has an existing file path.
    """

    path = Path(path_str)
    path.touch(exist_ok=True)

    return path
