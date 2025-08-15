from skelo_ai.inference import SketchLogic
from skelo_ai.wires import detect_wires
from skelo_ai.draw import render_circuit
from pathlib import Path
import json

class CircuitParser():
    def load_model(self):
        # PREPARATION
        model_path = Path("skelo_ai/SKELOv1.pt")
        self.model = SketchLogic(model_path)

    def parse_circuit(self, file_path: str, debug=False) -> dict:
        # GET GATES INFO
        gate_results = self.model.infer(file_path, debug=True)
        # model.visualize(results)
        if debug: print('infer done')
        gate_results = self.model.format_results(gate_results)['annotations']
        if debug: print('format done')
        # GET WIRES INFO
        gate_wire_results = detect_wires(file_path, gate_results, debug=True)
        if debug: print('wires done')

        # with open('z_output.json', 'w') as file:
        #     json.dump(gate_wire_results, file, indent=4)

        # VISUALIZE
        # print(gate_wire_results)
        rendered_image = render_circuit(gate_wire_results, "z_output.jpg", "white", 40)
        if debug: print('render done')

        return gate_wire_results, rendered_image

def main() -> None:
    """ Test driver """
    # parse_circuit("skelo_ai/inputs/3.jpg")

if __name__ == "__main__":
    main()