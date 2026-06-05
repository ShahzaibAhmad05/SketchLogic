from pathlib import Path
import sys
from inference import infer


def main() -> int:
    """
    Entry point for the model system.
    """

    args = sys.argv[1:]
    if not args or len(args) != 3:
        print("Insufficient arguments provided.")
        print("Usage: model.exe <input_image_path> <output_directory_path>")
        return -1
    
    image_path = Path(args[0])
    if not image_path.exists():
        print(f"Image file does not exist: {image_path}")
        return -1

    output_path = Path(args[1])
    if output_path.is_file():
        print(f"Output path is not a directory: {output_path}")
        return -1
    
    output_path.mkdir(parents=True, exist_ok=True)

    infer(image_path, output_path)
    return 0


if __name__ == "__main__":
    main()
