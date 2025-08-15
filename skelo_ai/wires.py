import cv2
import numpy as np
from skimage.morphology import skeletonize
from skimage.util import invert
from ultralytics import YOLO
import uuid
import math
import time
from scipy.spatial import cKDTree
import json
import copy

def change_resolution(image, scale):
    width = int(image.shape[1] * scale)
    height = int(image.shape[0] * scale)
    resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

    return resized

def binarize_and_skeletonize(image):
    # Step 1: Load image to grey
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # Step 4: Convert to boolean and invert (skeletonize works on white lines on black)
    binary_bool = binary == 0  # True where black (line), False elsewhere
    skeleton = skeletonize(binary_bool)
    skeleton_image = (skeleton * 255).astype(np.uint8)

    return skeleton_image

def blacken_gate_boxes(image, gates, scale=1.0):
    for gate in gates:
        x = int(gate['x'] * scale)
        y = int(gate['y'] * scale)
        w = int(gate['width'] * scale)
        h = int(gate['height'] * scale)

        image[y:y+h, x:x+w] = 0  # Set region to black

    return image

def point_distance_to_box(point, bbox) -> int:
    px, py = point
    bx, by = bbox['x'], bbox['y']
    bw, bh = bbox['width'], bbox['height']

    # Box boundaries
    left   = bx
    right  = bx + bw
    top    = by
    bottom = by + bh

    # Check if point is inside the box
    if left <= px <= right and top <= py <= bottom:
        return -1
    # Calculate horizontal and vertical distances
    dx = max(left - px, 0, px - right)
    dy = max(top - py, 0, py - bottom)
    # Return nearest distance
    return int(round(math.hypot(dx, dy)))

def filter_white_pixels(binary_image):
    y_coords, x_coords = np.where(binary_image == 255)
    white_pixels = [(int(x), int(y)) for x, y in zip(x_coords, y_coords)]
    return white_pixels

def draw_annotations(image, points=None, rectangles=None, lines=None, output_path="output.jpg"):
    img_copy = image.copy()

    # Draw points (small red circles)
    if points:
        for (x, y) in points:
            cv2.circle(img_copy, (int(x), int(y)), radius=3, color=(0, 0, 255), thickness=-1)
    # Draw rectangles (green)
    if rectangles:
        for rect in rectangles:
            x1, y1 = int(rect['x']), int(rect['y'])
            x2, y2 = x1 + int(rect['width']), y1 + int(rect['height'])
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), color=(0, 255, 0), thickness=2)
    # Draw lines (blue)
    if lines:
        for (pt1, pt2) in lines:
            x1, y1 = map(int, pt1)
            x2, y2 = map(int, pt2)
            cv2.line(img_copy, (x1, y1), (x2, y2), color=(255, 0, 0), thickness=2)
    # Save result
    cv2.imwrite(output_path, img_copy)

def filter_close_pixels(pixels, threshold=10):
    filtered = []
    for p in pixels:
        current = p  # third value and round coords
        # Skip if too close to any already accepted point
        too_close = any(distance((current[0], current[1]), existing) <= threshold for existing in filtered)
        if not too_close:
            filtered.append(current)

    return filtered

def distance(p1, p2):
    """Calculate Euclidean distance between two 2D points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def get_gate_connections(gates, pixels, terminal_threshold=5):
    for gate in gates:
        connected_pixels = []

        for pixel in pixels:
            if point_distance_to_box(pixel, gate) < terminal_threshold:
                connected_pixels.append(pixel)

        connected_pixels = filter_close_pixels(connected_pixels, threshold=10)
        gate['connected_pixels'] = connected_pixels
    return gates

def average_of_pixels(pixels):
    average = [0, 0]

    for pixel in pixels:
        average[0] += pixel[0]
        average[1] += pixel[1]
    average[0] = int(average[0] / len(pixels))
    average[1] = int(average[1] / len(pixels))
    average = (average[0], average[1])
    return average

def get_connections_info(gates, pixels, vision_threshold=10, max_points_skip=5):
    # Initialize k-d tree for fast spatial queries
    pixel_array = np.array(pixels)  # (N, 2)
    pixel_tree = cKDTree(pixel_array)

    for gate in gates:
        connected_wires = []

        # An agent walks along the average of the pixels
        for starting_point in gate['connected_pixels']:
            stepped_pixels = set()
            connected_cluster = [starting_point]
            average_point = None

            while True:
                closest_pixels = []
                if average_point is None: 
                    average_point = starting_point

                # stepped_pixels should now be a set for O(1) lookups
                nearby_indices = pixel_tree.query_ball_point(average_point, r=vision_threshold)

                closest_pixels = []
                for idx in nearby_indices:
                    point = tuple(pixel_array[idx])
                    if point not in stepped_pixels:
                        closest_pixels.append(point)
                        stepped_pixels.add(point)

                if len(closest_pixels) == 0:
                    connected_cluster.append('null')
                    break
                average_point = average_of_pixels(closest_pixels)

                break_flag = False
                for new_gate in gates:
                    if point_distance_to_box(average_point, new_gate) < vision_threshold:
                        if gate != new_gate:
                            connected_cluster.append(average_point)
                            break_flag = True
                            break
                if break_flag: 
                    for new_gate in gates:
                        if new_gate == gate: continue
                        for new_point in new_gate['connected_pixels']:
                            if distance(new_point, average_point) < vision_threshold:
                                connected_cluster.append(new_point)
                                connected_cluster.append((new_gate['id']))
                                break
                    break
                else: connected_cluster.append(average_point)

            temp = []
            if len(connected_cluster) > 15:
                for i, point in enumerate(connected_cluster):
                    if i == 0 or i == len(connected_cluster) - 1:
                        temp.append(point)  # Always include start and end
                    elif i % max_points_skip == 0:
                        temp.append(point)
                        
            connected_wires.append(temp)

        gate['connections'] = connected_wires
    # Delete temp data
    for gate in gates:
        del gate['connected_pixels']

    # for gate in gates:
    #     print('___ NEW GATE ___')
    #     for cluster in gate['connections']:  # This gets the correct wires per gate
    #         print(cluster)
    return gates

def set_input_output_info(gates, inputs_gap_threshold=100):
    # Check which terminals are close to each other
    # Do this for each gate
    # Mark as input or output at index 0
    for gate in gates:
        if gate['type'] == 'NOT': 
            found_output_flag = False
            for cluster in gate['connections']:
                if cluster[-1] != 'null':
                    cluster.insert(0, 'output')
                    for cluster2 in gate['connections']:
                        if cluster2 != cluster:
                            cluster2.insert(0, 'input')
                            found_output_flag = True
                            break
                    break
            if found_output_flag: continue

            gate_center_point = average_of_pixels([(gate['x'], gate['y']), (gate['x'] + gate['width'], 
                                                  gate['y'] + gate['height'])])
            if (distance(gate_center_point, gate['connections'][0][0]) <
                distance(gate_center_point, gate['connections'][1][0])):
                gate['connections'][0].insert(0, 'input')
                gate['connections'][1].insert(0, 'output')
            else:
                gate['connections'][1].insert(0, 'input')
                gate['connections'][0].insert(0, 'output')
            continue
        if len(gate['connections']) == 0:
            continue
        wire_starting_points = []
        for cluster in gate['connections']:
            if cluster:
                wire_starting_points.append(cluster[0])
        
        inputs = []
        # Filter inputs based on threshold
        while True:
            for pixel1 in wire_starting_points:
                for pixel2 in wire_starting_points:
                    if pixel1 == pixel2: continue

                    gap = distance(pixel1, pixel2)
                    if gap < inputs_gap_threshold:
                        if pixel1 not in inputs: inputs.append(pixel1)
                        if pixel2 not in inputs: inputs.append(pixel2)
            
            if len(inputs) == len(wire_starting_points) - 1:
                break
            else:
                inputs_gap_threshold += 25

        for cluster in gate['connections']:
            if cluster:
                if cluster[0] in inputs:
                    cluster.insert(0, 'input')
                else:
                    cluster.insert(0, 'output')

    # for gate in gates:
    #     print('___ NEW GATE ___')
    #     for cluster in gate['connections']:  # This gets the correct wires per gate
    #         print(cluster)

    return gates

def process_wires(gates):
    built_wires = []
    gate_connected_wires = []

    wires = []
    for gate in gates:
        gate['connected_wires'] = []    # This is useful later
        for cluster in gate['connections']:
            cluster.insert(0, gate['id'])
            wires.append(cluster)

    # Add both ends info
    processed_wires = []
    for wire in wires:
        for wire2 in wires:
            if wire == wire2: continue
            elif wire in processed_wires or wire2 in processed_wires: continue
            elif len(wire2) == 2 and distance(wire[2], wire2[-2]) < 50:
                wire.insert(-1, wire2[1])
                wire2.insert(-1, wire[1])
                processed_wires.append(wire)
                processed_wires.append(wire2)

    # Add the info to gates variable
    # Process the returnee variable
    returning_wires = {}
    for wire in wires:
        wire_id = str(uuid.uuid4())
        end_index = -1 if wire[-1] == 'null' else -2
        wire_points = wire[2:end_index]
        returning_wires[wire_id] = wire_points

        for gate in gates:
            if gate['id'] == wire[0] and len(wire) > 1:
                if wire[1] == 'input':
                    gate['connected_wires'].insert(0, wire_id)
                else: gate['connected_wires'].append(wire_id)
    # Cleanup and corrections
    for gate in gates:
        gate['num_inputs'] = max(1, len(gate['connected_wires']) - 1)
        # del gate['connections']
        if gate.get('confidence') is not None:
            del gate['confidence']

    # Cleanup gate connections
    for gate in gates:
        new_gate_connections = []
        for connection in gate['connections']:
            if len(connection) > 2: new_gate_connections.append([connection[0], connection[1], connection[-1]])
        
        gate['connections'] = new_gate_connections

    # for wire, points in returning_wires.items(): 
    #     print(wire)
    #     print(points)
    # for gate in gates:
    #     print('___ NEW GATE ___')
    #     print(gate)

    return returning_wires


def add_toggles_probes(prev_results) -> dict:
    probes_to_add = set()
    toggles_to_add = set()

    for gate in prev_results['gates']:
        for idx, connection in enumerate(gate['connections']):
            if connection[-1] == 'null':

                if connection[1] == 'input': 
                    connection[-1] = 'probe'

                    for wire in prev_results['wires'].keys():
                        if wire == gate['connected_wires'][idx]:
                            points_to_add = (prev_results['wires'][wire][-2], prev_results['wires'][wire][-1])
                            probes_to_add.add(points_to_add)
                            break

                elif connection[1] == 'output': 
                    connection[-1] = 'toggle'

                    for wire in prev_results['wires'].keys():
                        if wire == gate['connected_wires'][idx]:
                            points_to_add = (prev_results['wires'][wire][-2], prev_results['wires'][wire][-1])
                            toggles_to_add.add(points_to_add)
                            break

    prev_results['probes'] = []
    prev_results['toggles'] = []
    for probe in probes_to_add:
        prev_results['probes'].append(probe)
    for toggle in toggles_to_add:
        prev_results['toggles'].append(toggle)

    # Cleanup
    for gate in prev_results['gates']:
        if gate.get('connections') is not None:
            # del gate['connections']
            pass
    return prev_results

def set_gate_rotations(gates):
    for gate in gates:
        gate_type = gate['type'].split('_')
        gate['type'] = gate_type[0]
        gate['rotation'] = int(gate_type[-1])
    return gates

def wires_detection_system(image_path, detected_gates, plot_images=False, save_json=False, debug=False) -> dict:
    raw_image = cv2.imread(image_path)
    image = binarize_and_skeletonize(raw_image)
    image = blacken_gate_boxes(image, detected_gates)

    pixels = filter_white_pixels(image)
    gates = get_gate_connections(detected_gates, pixels)
    gates = get_connections_info(gates, pixels)
    gates = set_input_output_info(gates)
    wires = process_wires(gates)
    gates = set_gate_rotations(gates)
    
    results = {
        'gates': gates,
        'wires': wires
    }
    updated_results = add_toggles_probes(results)
    # results = rescale_logic_layout(results, 0.5, 0.5, toggle_positions, probe_positions)
    # print(results)
    if save_json:
        with open('z_output.json', 'w') as file:
            json.dump(updated_results, file, indent=4)
    # json_data = json.dumps(results)
    # xml_data = convert_json_to_xml('z_output.json', 'z_output.xml')
    # with open('z_output.xml', 'w') as file:
    #     xml_data.write(file)

    collected_points = []
    for _, points in wires.items():
        for point in points:
            collected_points.append(point)

    if plot_images:
        draw_annotations(raw_image, points=collected_points, rectangles=detected_gates, 
                        output_path="z_output.jpg")
        
    return results
    
def detect_wires(image_path, gate_results: dict, debug=False) -> dict:
    results = wires_detection_system(image_path, gate_results, debug=debug)
    return results

def main():
    """ Test Driver """
    image_path = "skelo_ai/inputs/3.jpg"
    gate_results = detect_wires(image_path, gate_results={})
    detect_wires(image_path, gate_results)

if __name__ == "__main__":
    main()