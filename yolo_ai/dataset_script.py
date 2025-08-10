"""
Prepare YOLO dataset (images + labels + data.yaml) from your updated JSON schema.

Hardcoded config:
  - IMAGES_DIR = raw_data/images
  - ANNOTATIONS_DIR = raw_data/annotations
  - OUTPUT_DIR = dataset_yolo
  - TRAIN_SPLIT = 0.85
  - SEED = 42
"""

import json
import shutil
from pathlib import Path
from typing import List, Tuple

# --- Hardcoded config ---
IMAGES_DIR = Path("yolo_ai/raw_data/images")
ANNOTATIONS_DIR = Path("yolo_ai/raw_data/annotations")
OUTPUT_DIR = Path("yolo_ai/dataset_yolo")
TRAIN_SPLIT = 0.85
SEED = 42
CLEAN_OUTPUT = True  # delete OUTPUT_DIR before writing

# --- light dependency bootstrap (Colab-friendly) ---
try:
    from PIL import Image
    import yaml
    from sklearn.model_selection import train_test_split
except Exception:
    import sys, subprocess
    print("Installing dependencies (pillow, pyyaml, scikit-learn)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pillow", "pyyaml", "scikit-learn"])
    from PIL import Image
    import yaml
    from sklearn.model_selection import train_test_split

# --- Classes: 7 types × 4 rotations ---
GATE_TYPES = ['AND', 'OR', 'NOT', 'NAND', 'NOR', 'XOR', 'XNOR']
ROTATIONS = [0, 90, 180, 270]
CLASSES = [f"{g}_{r}" for g in GATE_TYPES for r in ROTATIONS]
CLASS_TO_ID = {name: i for i, name in enumerate(CLASSES)}

def normalize_rotation(rot: int) -> int:
    r = int(round(rot / 90.0) * 90) % 360
    return r if r in (0, 90, 180, 270) else 0

def convert_bbox_to_yolo(x, y, w, h, img_w, img_h) -> Tuple[float, float, float, float]:
    cx = (x + w / 2.0) / img_w
    cy = (y + h / 2.0) / img_h
    wn = w / img_w
    hn = h / img_h
    return cx, cy, wn, hn

def yolo_lines_from_json(json_path: Path, img_w: int, img_h: int) -> List[str]:
    with open(json_path, "r") as f:
        data = json.load(f)

    # schema:
    # {
    #   "filename": "0001.png",
    #   "annotations": [{id, type, x, y, width, height, rotation}, ...]
    # }
    lines = []
    for ann in data.get("annotations", []):
        gate_type = str(ann.get("type", "")).upper()
        if gate_type not in GATE_TYPES:
            continue
        rot = normalize_rotation(int(ann.get("rotation", 0)))
        cls_name = f"{gate_type}_{rot}"
        cls_id = CLASS_TO_ID.get(cls_name, None)
        if cls_id is None:
            continue

        # clamp bbox to image bounds
        x = float(ann["x"]); y = float(ann["y"])
        w = float(ann["width"]); h = float(ann["height"])
        x = max(0.0, x); y = max(0.0, y)
        x2 = min(x + w, img_w); y2 = min(y + h, img_h)
        w = max(0.0, x2 - x); h = max(0.0, y2 - y)
        if w <= 0 or h <= 0:
            continue

        cx, cy, wn, hn = convert_bbox_to_yolo(x, y, w, h, img_w, img_h)
        # clamp to [0,1]
        cx = max(0, min(1, cx)); cy = max(0, min(1, cy))
        wn = max(0, min(1, wn)); hn = max(0, min(1, hn))

        lines.append(f"{cls_id} {cx:.6f} {cy:.6f} {wn:.6f} {hn:.6f}")
    return lines

def collect_images(images_dir: Path) -> List[Path]:
    exts = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
    files = [p for p in images_dir.iterdir() if p.suffix.lower() in exts and p.is_file()]
    files.sort()
    return files

def write_data_yaml(root: Path):
    data = {
        "path": str(root.resolve()),
        "train": "images/train",
        "val": "images/val",
        "nc": len(CLASSES),
        "names": CLASSES,
    }
    with open(root / "data.yaml", "w") as f:
        yaml.dump(data, f, sort_keys=False)

def make_dirs(root: Path):
    for p in [root/"images"/"train", root/"images"/"val", root/"labels"/"train", root/"labels"/"val"]:
        p.mkdir(parents=True, exist_ok=True)

def main():
    if CLEAN_OUTPUT and OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    make_dirs(OUTPUT_DIR)

    img_files = collect_images(IMAGES_DIR)
    if not img_files:
        raise SystemExit(f"No images found in {IMAGES_DIR}")

    # simple random split (rotations are NOT separate files)
    train_files, val_files = train_test_split(
        img_files, train_size=TRAIN_SPLIT, random_state=SEED, shuffle=True
    )

    def process_split(files: List[Path], split: str):
        im_out = OUTPUT_DIR / "images" / split
        lb_out = OUTPUT_DIR / "labels" / split
        missing_json = 0
        for img_path in files:
            json_path = ANNOTATIONS_DIR / f"{img_path.stem}.json"
            # get image size
            try:
                with Image.open(img_path) as im:
                    w, h = im.size
            except Exception as e:
                print(f"[warn] skipping bad image {img_path.name}: {e}")
                continue

            if json_path.exists():
                lines = yolo_lines_from_json(json_path, w, h)
            else:
                missing_json += 1
                lines = []  # write empty label -> background image

            shutil.copy2(img_path, im_out / img_path.name)
            (lb_out / f"{img_path.stem}.txt").write_text("\n".join(lines))

        if missing_json:
            print(f"[info] {missing_json} images in {split} had no JSON; wrote empty labels.")

    process_split(train_files, "train")
    process_split(val_files, "val")
    write_data_yaml(OUTPUT_DIR)

    print("✅ Dataset ready.")
    print(f"Total images: {len(img_files)} | Train: {len(train_files)} | Val: {len(val_files)}")
    print(f"data.yaml -> {OUTPUT_DIR/'data.yaml'}")
    print(f"Classes ({len(CLASSES)}): {CLASSES}")

if __name__ == "__main__":
    main()
