"""
Controller file for circuit parsing used by Flask api.

"""

from pathlib import Path
from PIL import Image
import sys
import json
try:
    from skelo.inference import SketchLogic
    from skelo.wires import detect_wires
    from skelo.label import draw_circuit_on_image
    from skelo.normalizer import *
except:
    print("Modular Imports Failed, trying to import directly...")
    from inference import SketchLogic
    from wires import detect_wires
    from label import draw_circuit_on_image
    from normalizer import *
    print("Success")

class CircuitParser():
    def __init__(self, model_path: Path) -> None:
        self.model = None
        self.model_path = model_path

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
        # Normalize
        # gate_wire_results = normalize_output(gate_wire_results)
        # finalized_results = convert_to_simulator_format(gate_wire_results)
        # finalized_results = normalize_wire_points(finalized_results)
        # finalized_results = relocate_circuit(finalized_results)
        # finalized_results = snap_coords_to_grid(finalized_results, grid_size=10.0)
        # finalized_results = remove_duplicate_points(gate_wire_results)
        # finalized_results = remove_close_points(finalized_results, threshold=10.0)
        print(gate_wire_results)
        rendered_image = draw_circuit_on_image(file_path, gate_wire_results)

        # For Debugging Purposes
        # rendered_image.show()
        with open('circuit.json', 'w') as file:
            json.dump(gate_wire_results, file, indent=4)

        return (gate_wire_results, rendered_image)

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