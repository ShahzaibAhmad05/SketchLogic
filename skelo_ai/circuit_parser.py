from inference import SketchLogic
from wires import detect_wires
from pathlib import Path
import json


def parse_circuit(file_path: str) -> dict:
    # PREPARATION
    model_path = Path("skelo_ai/SKELOv1n.pt")
    model = SketchLogic(model_path)

    # GET GATES INFO
    gate_results = model.infer(file_path, debug=True)
    # model.visualize(results)
    gate_results = model.format_results(gate_results)['annotations']
    # GET WIRES INFO
    gate_wire_results = detect_wires(file_path, gate_results, debug=True)

    with open('z_output.json', 'w') as file:
        json.dump(gate_wire_results, file, indent=4)



    return gate_wire_results

def main() -> None:
    """ Test driver """
    parse_circuit("skelo_ai/inputs/3.jpg")

if __name__ == "__main__":
    main()