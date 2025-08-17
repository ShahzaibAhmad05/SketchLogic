"""
Controller file for circuit parsing used by Flask api

"""

from skelo_ai.inference import SketchLogic
from skelo_ai.wires import detect_wires
from skelo_ai.label import draw_circuit_on_image
from pathlib import Path
from PIL import Image
import sys

class CircuitParser():
    def __init__(self) -> None:
        self.model = None
        self.model_path = Path("skelo_ai/SKELOv1.pt")

    def load_model(self) -> None:
        self.model = SketchLogic(self.model_path)

    def parse_circuit(self, file_path: str) -> tuple[dict, Image.Image]:
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
        gate_results = self.model.format_results(gate_results)['annotations']
        # GET WIRES INFO
        gate_wire_results = detect_wires(file_path, gate_results)
        # VISUALIZE
        rendered_image = draw_circuit_on_image(file_path, gate_wire_results)

        return (gate_wire_results, rendered_image)

def main() -> None:
    """ Test driver """
    engine = CircuitParser()
    engine.load_model()
    test_image_path = Path("example.jpg")

    # Make sure the test image is present
    if test_image_path.exists():
        engine.parse_circuit(test_image_path.absolute())
    else:
        print("Test image not found")

if __name__ == "__main__":
    main()