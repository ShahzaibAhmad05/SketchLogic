"""
Controller file for circuit parsing used by Flask api.

For debugging purposes, please use the backend API with testRun.py or frontend.

"""

from pathlib import Path
from PIL import Image
import sys, cv2
from skelo.inference import SketchLogic
from skelo.wires import wires_detection_system


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
        img = cv2.imread(file_path)
        gate_results = self.model.infer(img=img)
        # GET WIRES INFO
        gate_wire_results = wires_detection_system(raw_image=img, 
                                                   detected_gates=gate_results)

        # Uncomment For Debugging Purposes
        # rendered_image.show()
        # with open('circuit.json', 'w') as file:
        #     json.dump(gate_wire_results, file, indent=4)

        return gate_wire_results
