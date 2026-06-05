from pathlib import Path
import sys


def main() -> int:
    """
    Entry point for the model system.
    """

    args = sys.argv[1:]
    if not args or len(args) != 3:
        print("Insufficient arguments provided.")
        print("Usage: model.exe <input_image_path> <output_json_path>")
        return -1
    
    image_path = Path(args[0])
    if not image_path.exists():
        print(f"Image file does not exist: {image_path}")
        return -1

    output_json_path = Path(args[1])
    if not output_json_path.is_file():
        print(f"Output JSON path is not a file: {output_json_path}")
        return -1
    
    from inference import infer
    infer(image_path, output_json_path)

    return 0


if __name__ == "__main__":
    main()
