from skelo_ai import SketchLogic
from pathlib import Path

def parse_circuit(file_path: str):
    # PREPARATION
    model_path = Path("skelo_ai/SKELOv1n.pt")
    model = SketchLogic(model_path)

    # GET GATES INFO
    results = model.infer(file_path, debug=True)
    model.visualize(results)
    gate_results = model.format_results(results, "skelo_ai/results.json")

    # GET WIRES INFO
    

    return gate_results

def main() -> None:
    """ Test driver """
    parse_circuit("skelo_ai/inputs/3.jpg")

if __name__ == "__main__":
    main()