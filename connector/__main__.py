import sys
from pathlib import Path
import json


def main() -> int:
    """
    Entry point for the connector system.
    """
    
    args = sys.argv[1:]

    result = verify_args(args)
    if result < 0:
        return result
    
    image_path = Path(args[0])
    model_results_json_path = Path(args[1])
    output_json_path = Path(args[2])

    from connecter import connect
    from converter import convert

    results = connect(image_path, model_results_json_path)
    converted_results = convert(results)

    with open(output_json_path, "w") as file:
        json.dump(converted_results, file, indent=4)

    return 0


def verify_args(args: list[str]) -> int:
    """
    Verifies if the arguments are exactly as expected.

    Returns:
        int: >=0 if the arguments are correct.
    """

    if not args or len(args) != 3:
        print("Insufficient arguments provided.")
        print("Usage: connector.exe <input_image_path> <model_results_json_path> <output_json_path>")
        return -1
    
    image_path = Path(args[0])
    if not image_path.exists():
        print(f"Image file does not exist: {image_path}")
        return -1

    model_results_json_path = Path(args[1])
    if not model_results_json_path.is_file():
        print(f"Model results JSON path is not a file: {model_results_json_path}")
        return -1

    output_json_path = Path(args[2])
    if not output_json_path.is_file():
        print(f"Output JSON path is not a file: {output_json_path}")
        return -1

    return 0


if __name__ == "__main__":
    main()
