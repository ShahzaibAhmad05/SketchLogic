"""
Controller file for circuit parsing used by Flask api.

Direct run is only allowed for Debugging purposes, otherwise, 
please use the backend API with testRun.py or frontend.

"""

from pathlib import Path
from PIL import Image
import sys
import json
try:
    from skelo.inference import SketchLogic
    from skelo.wires import detect_wires
    from skelo.normalizer import *
except:
    print("Modular Imports Failed, trying to import directly...")
    from inference import SketchLogic
    from wires import detect_wires
    from normalizer import *
    print("Success")


class CircuitParser():
    def __init__(self, model_path: Path) -> None:
        self.model = None
        self.model_path = model_path

    def load_model(self) -> None:
        self.model = SketchLogic(self.model_path)

    def parse_circuit(self, file_path: str) -> dict:
        if self.model is None:
            print("[ERROR] model is not loaded")
            print("Please load the model before calling parse_circuit()")
            print("Call load_model() to load the model")
            sys.exit(1)

        # PATCH: if it is PIL Image
        if isinstance(file_path, Image.Image):
            file_path.save("temp.jpg")
            file_path = "temp.jpg"

        # GET GATES INFO
        gate_results = self.model.infer(file_path)
        # GET WIRES INFO
        gate_wire_results = detect_wires(file_path, gate_results)

        # Uncomment For Debugging Purposes
        # rendered_image.show()
        # with open('circuit.json', 'w') as file:
        #     json.dump(gate_wire_results, file, indent=4)

        return gate_wire_results


def main() -> None:

    if input("Direct run is only allowed for debugging purposes..."
                "\nDo you wish to proceed? (y) ") not in ["Y", "y"]:
        sys.exit(0)

    engine = CircuitParser('skelo/SKELOv1.pt')
    engine.load_model()
    test_image_path = Path("example.jpg")

    # Make sure the test image is present
    if test_image_path.exists():
        engine.parse_circuit(str(test_image_path))
    else:
        print("Test image not found")

if __name__ == "__main__":
    main()