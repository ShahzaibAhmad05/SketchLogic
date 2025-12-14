""" A script for converting the output of the wires detection system to a format compatible with the simulator """

# TODO: remove the unused ones
import cv2
import numpy as np
from skimage.morphology import skeletonize
import uuid
import math
from scipy.spatial import cKDTree


def convert_to_simulator_format(data: dict) -> dict:
    """
    Convert extracted circuit JSON (with gates + wires)
    into simulator JSON (with Components + Wires).
    """

    # Mapping between your gate types and simulator names
    gate_type_map = {
        "AND": "AndGate",
        "OR": "OrGate",
        "NOT": "NotGate",
        "XOR": "XorGate",
        "NAND": "NandGate",
        "NOR": "NorGate"
    }

    components = []
    wires = []

    # --- Convert Gates ---
    for gate in data.get("gates", []):
        g_type = gate_type_map.get(gate["type"], gate["type"])
        num_inputs = gate.get("num_inputs", 0)

        terminals = []
        wire_ids = gate.get("connected_wires", [])

        # Input terminals (placed on left side with Y offsets)
        for i in range(num_inputs):
            terminals.append({
                "Position": {"X": -20.0, "Y": 20.0 + i * 20.0},
                "ConnectedWireIds": [wire_ids[i]] if i < len(wire_ids) else []
            })

        # Output terminal (always last, on right side)
        if len(wire_ids) > num_inputs:
            output_wire = wire_ids[num_inputs]
        else:
            output_wire = None

        terminals.append({
            "Position": {"X": 80.0, "Y": 30.0},
            "ConnectedWireIds": [output_wire] if output_wire else []
        })

        components.append({
            "Type": g_type,
            "Terminals": terminals,
            "InputLineCount": num_inputs,
            "SelectionLineCount": 0,
            "X": float(gate["x"]),
            "Y": float(gate["y"]),
            "StoredStates": {},
            "Rotation": float(gate.get("rotation", 0)),
            "IsSelected": False
        })

    # --- Convert Wires ---
    for wire_id, points in data.get("wires", {}).items():
        wires.append({
            "Id": wire_id,
            "Value": None,
            "Points": [{"X": float(x), "Y": float(y)} for x, y in points]
        })

    return {"Components": components, "Wires": wires}

def find_min_coords(data: dict) -> tuple[int, int, int, int]:
    """ 
    Returns the minimum x and y coordinates from components and wires 
    
    """
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = float('-inf'), float('-inf')

    for component in data["Components"]:
        min_x = min(min_x, component["X"])
        min_y = min(min_y, component["Y"])

        max_x = max(max_x, component["X"])
        max_y = max(max_y, component["Y"]) 

    for point in data["Wires"]["Points"]: 
        min_x = min(min_x, min(point["X"]))
        min_y = min(min_y, min(point["Y"]))

        max_x = max(max_x, max(point["X"]))
        max_y = max(max_y, max(point["Y"]))

    return (min_x, min_y, max_x, max_y)

def find_reduc_factor(data: dict) -> dict:
    pass

def normalize_output(data: dict) -> dict:
    target_w, target_h = 65, 60
    # Use first gate as reference for global scaling
    try:
        ref_gate = data["gates"][0]
    except: # Fallback
        return data
    scale_x = target_w / ref_gate["width"]
    scale_y = target_h / ref_gate["height"]

    # Update gates
    for gate in data["gates"]:
        gate["x"] = int(gate["x"] * scale_x)
        gate["y"] = int(gate["y"] * scale_y)
        gate["width"] = target_w
        gate["height"] = target_h

    # Update wires
    for wire_id, coords in data["wires"].items():
        new_coords = []
        for x, y in coords:
            new_coords.append([int(x * scale_x), int(y * scale_y)])
        data["wires"][wire_id] = new_coords

    return data
 


import math
from typing import Dict, List

def angle_between(v1, v2):
    """Return angle in degrees between two vectors."""
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
    if mag1 == 0 or mag2 == 0:
        return 0
    cos_theta = max(-1, min(1, dot / (mag1 * mag2)))
    return math.degrees(math.acos(cos_theta))

def normalize_wire_points(data: Dict) -> Dict:
    new_wires = []
    for wire in data.get("Wires", []):
        pts = wire["Points"]
        if len(pts) <= 2:
            new_wires.append(wire)
            continue

        simplified = [pts[0]]  # keep first point
        for i in range(1, len(pts) - 1):
            prev_pt = pts[i - 1]
            curr_pt = pts[i]
            next_pt = pts[i + 1]

            v1 = (curr_pt["X"] - prev_pt["X"], curr_pt["Y"] - prev_pt["Y"])
            v2 = (next_pt["X"] - curr_pt["X"], next_pt["Y"] - curr_pt["Y"])

            if angle_between(v1, v2) >= 45:  # keep if angle ≥ 45°
                simplified.append(curr_pt)

        simplified.append(pts[-1])  # keep last point
        wire["Points"] = simplified
        new_wires.append(wire)

    data["Wires"] = new_wires
    return data

def relocate_circuit(data: Dict) -> Dict:
    window_w, window_h = 1280, 720
    center_x, center_y = window_w / 2, window_h / 2

    # Collect all coordinates
    xs, ys = [], []

    for comp in data.get("Components", []):
        xs.append(comp["X"])
        ys.append(comp["Y"])
        for term in comp.get("Terminals", []):
            xs.append(term["Position"]["X"] + comp["X"])
            ys.append(term["Position"]["Y"] + comp["Y"])

    for wire in data.get("Wires", []):
        for pt in wire.get("Points", []):
            xs.append(pt["X"])
            ys.append(pt["Y"])

    if not xs or not ys:
        return data  # nothing to center

    # Circuit bounding box center
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    circuit_cx = (min_x + max_x) / 2
    circuit_cy = (min_y + max_y) / 2

    # Offset to center
    dx = center_x - circuit_cx
    dy = center_y - circuit_cy

    # Apply shift
    for comp in data.get("Components", []):
        comp["X"] += dx
        comp["Y"] += dy
        for term in comp.get("Terminals", []):
            term["Position"]["X"] += dx
            term["Position"]["Y"] += dy

    for wire in data.get("Wires", []):
        for pt in wire.get("Points", []):
            pt["X"] += dx
            pt["Y"] += dy

    return data

import math
from typing import Dict, Any, List

def remove_close_points(data: Dict[str, Any], threshold: float = 5.0) -> Dict[str, Any]:
    """
    Remove points from wire paths that are too close together based on a distance threshold.
    
    Args:
        data: Circuit data dictionary containing Components and Wires
        threshold: Minimum distance between consecutive points (default: 5.0 pixels)
    
    Returns:
        Modified data dictionary with simplified wire points
    """
    def distance(p1: Dict[str, float], p2: Dict[str, float]) -> float:
        """Calculate Euclidean distance between two points"""
        dx = p1["X"] - p2["X"]
        dy = p1["Y"] - p2["Y"]
        return math.sqrt(dx * dx + dy * dy)
    
    def simplify_points(points: List[Dict[str, float]], threshold: float) -> List[Dict[str, float]]:
        """Remove consecutive points that are closer than threshold distance"""
        if len(points) <= 2:
            return points  # Keep all points if 2 or fewer
        
        simplified = [points[0]]  # Always keep the first point
        
        for i in range(1, len(points)):
            current_point = points[i]
            last_kept_point = simplified[-1]
            
            # If this is the last point, always keep it
            if i == len(points) - 1:
                simplified.append(current_point)
            # Otherwise, only keep if distance is above threshold
            elif distance(current_point, last_kept_point) >= threshold:
                simplified.append(current_point)
        
        return simplified
    
    # Create a deep copy of the data to avoid modifying the original
    result = {
        "Components": data.get("Components", []),
        "Wires": []
    }
    
    # Process each wire
    for wire in data.get("Wires", []):
        new_wire = {
            "Id": wire.get("Id"),
            "Value": wire.get("Value"),
            "Points": simplify_points(wire.get("Points", []), threshold)
        }
        result["Wires"].append(new_wire)
    
    return result

from typing import Dict, Any

def snap_coords_to_grid(data: Dict[str, Any], grid_size: int = 10) -> Dict[str, Any]:
    """
    Snap all coordinates in the circuit data to multiples of the grid size.
    
    Args:
        data: Circuit data dictionary containing Components and Wires
        grid_size: Grid size to snap to (default: 10)
    
    Returns:
        Modified data dictionary with snapped coordinates
    """
    def snap_value(value: float, grid_size: int) -> float:
        """Snap a value to the nearest multiple of grid_size"""
        return round(value / grid_size) * grid_size
    
    # Create a deep copy of the data
    result = {
        "Components": [],
        "Wires": []
    }
    
    # Process Components
    for component in data.get("Components", []):
        new_component = component.copy()
        
        # Snap component X, Y coordinates
        if "X" in new_component:
            new_component["X"] = snap_value(new_component["X"], grid_size)
        if "Y" in new_component:
            new_component["Y"] = snap_value(new_component["Y"], grid_size)
        
        # Snap terminal positions
        if "Terminals" in new_component:
            new_terminals = []
            for terminal in new_component["Terminals"]:
                new_terminal = terminal.copy()
                if "Position" in new_terminal:
                    position = new_terminal["Position"].copy()
                    if "X" in position:
                        position["X"] = snap_value(position["X"], grid_size)
                    if "Y" in position:
                        position["Y"] = snap_value(position["Y"], grid_size)
                    new_terminal["Position"] = position
                new_terminals.append(new_terminal)
            new_component["Terminals"] = new_terminals
        
        result["Components"].append(new_component)
    
    # Process Wires
    for wire in data.get("Wires", []):
        new_wire = {
            "Id": wire.get("Id"),
            "Value": wire.get("Value"),
            "Points": []
        }
        
        # Snap wire point coordinates
        for point in wire.get("Points", []):
            new_point = {
                "X": snap_value(point.get("X", 0), grid_size),
                "Y": snap_value(point.get("Y", 0), grid_size)
            }
            new_wire["Points"].append(new_point)
        
        result["Wires"].append(new_wire)
    
    return result

from typing import Dict, Any

def remove_duplicate_points(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove consecutive duplicate points from wire paths.
    
    Args:
        data: Circuit data dictionary containing Components and Wires
    
    Returns:
        Modified data dictionary with duplicate points removed
    """
    result = {
        "Components": data.get("Components", []),
        "Wires": []
    }
    
    for wire in data.get("Wires", []):
        points = wire.get("Points", [])
        
        if len(points) <= 1:
            # Keep wires with 0 or 1 points as-is
            result["Wires"].append(wire)
            continue
        
        # Remove consecutive duplicates
        filtered_points = [points[0]]  # Always keep first point
        
        for i in range(1, len(points)):
            current = points[i]
            previous = filtered_points[-1]
            
            # Only add if different from previous point
            if current["X"] != previous["X"] or current["Y"] != previous["Y"]:
                filtered_points.append(current)
        
        new_wire = {
            "Id": wire.get("Id"),
            "Value": wire.get("Value"),
            "Points": filtered_points
        }
        result["Wires"].append(new_wire)

        invalidWires = []
        for wire in result["Wires"]:
            if len(wire["Points"]) < 2:
                print(f"[WARNING] Wire {wire['Id']} has less than 2 points after removing duplicates.")
                invalidWires.append(wire)
        for wire in invalidWires:
            result["Wires"].remove(wire)
            print(f"[INFO] Removed wire {wire['Id']} due to insufficient points.")
    
    return result