import os
import cv2
import json

# --- CONFIGURATION ---
IMAGE_DIR = "yolo_ai/raw_data/images"
ANNOTATION_DIR = "yolo_ai/raw_data/annotations"

# Map number keys to gate types
gate_types = {
    ord('1'): 'AND',
    ord('2'): 'OR',
    ord('3'): 'NOT',
    ord('4'): 'NOR',
    ord('5'): 'NAND',
    ord('6'): 'XOR',
    ord('7'): 'XNOR'
}

# Allowed orthogonal angles
orth_angles = [0, 90, 180, 270]

# --- GLOBAL STATE ---
drawing = False
ix = iy = 0
current_box = None
current_angle = 0
current_type = 'AND'  # default gate type
annotations = []


def print_instructions():
    print("Instructions:")
    print(" Gate type: AND (press 1–7 to change, persists across images)")
    print(" Draw bounding box: click + drag (axis-aligned, auto-confirm on release)")
    print(" Rotate (metadata only): 'r'=rotate CCW 90°, 'e'=rotate CW 90° (persists across images)")
    print(" Undo last annotation: 'z'")
    print(" Save JSON manually: 's'")
    print(" Previous image (auto-saves): 'p'")
    print(" Next image (auto-saves): 'n'")
    print(" Help: 'h'")
    print(" Quit (auto-saves): 'q'\n")


def mouse_callback(event, x, y, flags, param):
    global drawing, ix, iy, current_box, current_angle, annotations
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        current_box = ((ix, iy), (x, y))
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        (x1, y1), (x2, y2) = (ix, iy), (x, y)
        # axis-aligned box coords
        x_min = min(x1, x2)
        y_min = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        ann = {
            'id': len(annotations) + 1,
            'type': current_type,
            'x': x_min,
            'y': y_min,
            'width': w,
            'height': h,
            'rotation': current_angle
        }
        annotations.append(ann)
        print(f"Added annotation {ann['id']} {ann['type']} @ rotation {ann['rotation']}° at ({ann['x']},{ann['y']})")
        current_box = None
        # current_angle persists for next box


def draw_annotations(img):
    display = img.copy()
    # Draw saved annotations as simple rectangles
    for ann in annotations:
        x, y = ann['x'], ann['y']
        w, h = ann['width'], ann['height']
        cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(display, f"{ann['id']}:{ann['type']} Rot:{ann['rotation']}°",
                    (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
    # Draw preview of current box (axis-aligned)
    if current_box:
        (x1, y1), (x2, y2) = current_box
        x_min = min(x1, x2)
        y_min = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        cv2.rectangle(display, (x_min, y_min), (x_min + w, y_min + h), (0, 0, 255), 2)
        cv2.putText(display, f"Type:{current_type} Rot:{current_angle}°",
                    (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
    return display


def save_annotations(img_name):
    os.makedirs(ANNOTATION_DIR, exist_ok=True)
    base = os.path.splitext(img_name)[0]
    out_path = os.path.join(ANNOTATION_DIR, f"{base}.json")
    data = {'filename': img_name, 'annotations': annotations}
    with open(out_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved annotations to {out_path}")


def main():
    global current_angle, current_type, annotations, current_box
    img_files = [f for f in os.listdir(IMAGE_DIR)
                 if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    img_files = sorted(img_files, key=lambda x: int(os.path.splitext(x)[0]))

    cv2.namedWindow('Annotator')
    cv2.setMouseCallback('Annotator', mouse_callback)

    print_instructions()

    idx = 0
    total = len(img_files)
    while 0 <= idx < total:
        img_name = img_files[idx]
        img = cv2.imread(os.path.join(IMAGE_DIR, img_name))
        if img is None:
            idx += 1
            continue

        annotations = []
        ann_path = os.path.join(ANNOTATION_DIR, f"{os.path.splitext(img_name)[0]}.json")
        if os.path.exists(ann_path):
            with open(ann_path, 'r') as f:
                annotations = json.load(f).get('annotations', [])
            print(f"Loaded {len(annotations)} existing annotations.")

        current_box = None
        # current_angle persists across images
        print(f"=== Annotating {img_name} ({idx+1}/{total}) ===")

        while True:
            disp = draw_annotations(img)
            cv2.imshow('Annotator', disp)
            key = cv2.waitKey(20) & 0xFF
            if key == 255:
                continue
            if key in gate_types:
                current_type = gate_types[key]
                print(f"Selected gate type: {current_type}")
            elif key == ord('r'):
                # rotate CCW
                current_angle = (current_angle - 90) % 360
                print(f"Rotation set to {current_angle}°")
            elif key == ord('e'):
                # rotate CW
                current_angle = (current_angle + 90) % 360
                print(f"Rotation set to {current_angle}°")
            elif key == ord('z'):
                if annotations:
                    removed = annotations.pop()
                    print(f"Removed annotation {removed['id']} {removed['type']}")
                else:
                    print("No annotations to undo.")
            elif key == ord('s'):
                save_annotations(img_name)
            elif key == ord('h'):
                print_instructions()
            elif key == ord('n'):
                save_annotations(img_name)
                print("Moving to next image...\n")
                idx += 1
                break
            elif key == ord('p'):
                save_annotations(img_name)
                if idx > 0:
                    print("Moving to previous image...\n")
                    idx -= 1
                else:
                    print("Already at first image.\n")
                break
            elif key == ord('q'):
                save_annotations(img_name)
                cv2.destroyAllWindows()
                return

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
