from ultralytics.models import YOLO
import sys
from pathlib import Path


def main():
    if (len(sys.argv) != 2 or not Path(sys.argv[1]).exists()):
        print("Usage: python to_onnx.py <model_path>")
        sys.exit(1)

    model = YOLO(sys.argv[1])
    model.export(format="onnx")


if __name__ == "__main__":
    main()
