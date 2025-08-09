import json
import os
from collections import defaultdict

def analyze_gates(annotations_dir):
    """
    Analyze gate types and rotations from JSON annotation files.
    
    Args:
        annotations_dir (str): Path to directory containing JSON annotation files
    """
    # Dictionary to store counts: gate_type -> rotation -> count
    gate_counts = defaultdict(lambda: defaultdict(int))
    total_files = 0
    total_gates = 0
    
    # Check if directory exists
    if not os.path.exists(annotations_dir):
        print(f"Error: Directory '{annotations_dir}' not found!")
        return
    
    # Process all JSON files in the directory
    for filename in os.listdir(annotations_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(annotations_dir, filename)
            total_files += 1
            
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Process annotations
                if 'annotations' in data:
                    for annotation in data['annotations']:
                        gate_type = annotation.get('type', 'UNKNOWN')
                        rotation = annotation.get('rotation', 0)
                        
                        gate_counts[gate_type][rotation] += 1
                        total_gates += 1
                        
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing {filename}: {e}")
                continue
    
    # Print results
    print(f"Analyzed {total_files} files with {total_gates} total gates\n")
    print("=" * 40)
    print()
    
    # Sort gate types alphabetically for consistent output
    for gate_type in sorted(gate_counts.keys()):
        rotations = gate_counts[gate_type]
        
        # Sort rotations numerically
        for rotation in sorted(rotations.keys()):
            count = rotations[rotation]
            print(f"{gate_type} with {rotation} angle => {count}")
        print()
    
    print("=" * 40)
    print()
    print("Summary by Gate Type:")
    
    # Print totals for each gate type
    for gate_type in sorted(gate_counts.keys()):
        total_for_type = sum(gate_counts[gate_type].values())
        print(f"{gate_type}: {total_for_type} gates")
    
    print("\nSummary by Rotation Angle:")
    
    # Count total gates for each rotation angle across all types
    rotation_totals = defaultdict(int)
    for gate_type in gate_counts:
        for rotation, count in gate_counts[gate_type].items():
            rotation_totals[rotation] += count
    
    for rotation in sorted(rotation_totals.keys()):
        print(f"{rotation}°: {rotation_totals[rotation]} gates")

    print()

if __name__ == "__main__":
    # Set the path to your annotations directory
    annotations_directory = "yolo_ai/raw_data/annotations"
    
    print()
    print("Gate Dataset Analysis Tool")
    print("=" * 40)
    print()
    
    analyze_gates(annotations_directory)