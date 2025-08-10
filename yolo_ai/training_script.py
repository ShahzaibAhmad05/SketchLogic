#!/usr/bin/env python3
"""
Train YOLOv10-s on the prepared dataset.

Hardcoded config:
  - DATA_YAML = dataset_yolo/data.yaml
  - MODEL = yolov10s.pt
  - EPOCHS = 120
  - IMGSZ = 640
  - BATCH = -1 (auto)
  - LR0 = 0.01
  - PATIENCE = 30
  - PROJECT = runs/train
  - RUN_NAME = logic_gates_yolov10s
Augmentations are orientation-safe (rotation is part of the class label),
so ALL orientation-changing augs are DISABLED (degrees/flip/shear/perspective).
"""

import shutil
from pathlib import Path

# --- Hardcoded config ---
DATA_YAML = Path("dataset_yolo/data.yaml")
MODEL = "yolov10s.pt"       # best balance for Colab T4
EPOCHS = 120
IMGSZ = 640
BATCH = -1                  # auto-batch
LR0 = 0.01
PATIENCE = 30
PROJECT = Path("runs/train")
RUN_NAME = "logic_gates_yolov10s"
SEED = 42

# --- light dependency bootstrap (Colab-friendly) ---
try:
    from ultralytics import YOLO
except Exception:
    import sys, subprocess
    print("Installing ultralytics==8.3.0 ...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "ultralytics==8.3.0"])
    from ultralytics import YOLO

def main():
    if not DATA_YAML.exists():
        raise SystemExit(f"data.yaml not found at {DATA_YAML}. Run prepare_dataset.py first.")

    print(f"Loading model: {MODEL}")
    model = YOLO(MODEL)

    results = model.train(
        data=str(DATA_YAML),
        epochs=EPOCHS,
        imgsz=IMGSZ,
        batch=BATCH,
        lr0=LR0,
        patience=PATIENCE,
        project=str(PROJECT),
        name=RUN_NAME,
        exist_ok=True,
        pretrained=True,
        seed=SEED,
        deterministic=False,
        single_cls=False,

        # Efficiency / stability
        rect=False,         # allow mosaic
        cos_lr=True,
        amp=True,
        device="auto",
        workers=2,          # safer on Colab
        cache="ram",

        # SAFE augmentations (do not change orientation)
        hsv_h=0.015, hsv_s=0.5, hsv_v=0.4,
        translate=0.08, scale=0.40,
        mosaic=0.50,        # moderate mosaic; reduce if VRAM tight
        close_mosaic=10,

        # CRITICAL: disable orientation-changing augs
        degrees=0.0, shear=0.0, perspective=0.0, flipud=0.0, fliplr=0.0,

        optimizer="AdamW",
        plots=True,
    )
    print("✅ Training finished.")

    # Save best weights at project root for convenience
    best_src = PROJECT / RUN_NAME / "weights" / "best.pt"
    if best_src.exists():
        shutil.copy2(best_src, "best_model.pt")
        print("Saved: best_model.pt")
    else:
        print(f"[warn] best.pt not found at {best_src}")

    # Optional quick val
    _ = model.val(data=str(DATA_YAML), imgsz=IMGSZ)

if __name__ == "__main__":
    main()
