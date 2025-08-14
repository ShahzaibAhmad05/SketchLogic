# yolo_ai/inference.py
from ultralytics import YOLO
import cv2
import os
from pathlib import Path
import torch
import glob
import numpy as np
import time

# --------- Config ---------
MODEL_PATH = "yolo_ai/best_model.pt"
INPUT_DIR  = "yolo_ai/inputs"
OUTPUT_DIR = "yolo_ai/outputs"

IMGSZ = 1024
CONF  = 0.25
IOU   = 0.70
WINDOW_NAME = "SketchLogic Detections"

MAX_DISPLAY_W = 1600
MAX_DISPLAY_H = 1000
# -------------------------

def ensure_dirs():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def list_images(folder):
    exts = ("*.jpg","*.jpeg","*.png","*.bmp","*.tif","*.tiff","*.webp")
    files = []
    for e in exts:
        files += glob.glob(str(Path(folder) / e))
    return sorted(files)

def class_color(cls_id: int):
    # stable pseudo-color per class (HSV->BGR)
    h = (cls_id * 0.61803398875) % 1.0
    s, v = 0.6, 1.0
    hsv = np.uint8([[[int(h*179), int(s*255), int(v*255)]]])
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0,0]
    return int(bgr[0]), int(bgr[1]), int(bgr[2])

def draw_caption(img, text):
    # semi-transparent top banner with text
    h, w = img.shape[:2]
    pad = max(6, int(0.006 * min(w, h)))
    fs  = max(0.5, min(1.0, 0.0006 * min(w, h)))
    th  = max(1, int(0.0025 * min(w, h)))
    (tw, th_text), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fs, th)
    bar_h = th_text + pad*2
    overlay = img.copy()
    cv2.rectangle(overlay, (0,0), (w, bar_h+2), (0,0,0), -1)
    img[:] = cv2.addWeighted(overlay, 0.35, img, 0.65, 0)
    cv2.putText(img, text, (pad, pad + th_text),
                cv2.FONT_HERSHEY_SIMPLEX, fs, (255,255,255), th, cv2.LINE_AA)

def draw_detections(img_bgr, result):
    h, w = img_bgr.shape[:2]
    names = result.names
    if result.boxes is None or len(result.boxes) == 0:
        cv2.putText(img_bgr, "No detections", (15, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 200, 255), 2, cv2.LINE_AA)
        return img_bgr

    xyxy = result.boxes.xyxy.cpu().numpy()
    confs = result.boxes.conf.cpu().numpy()
    clses = result.boxes.cls.cpu().numpy().astype(int)

    t = max(2, int(round(min(w, h) / 500)))
    fs = max(0.6, min(1.2, t * 0.5))

    for (x1, y1, x2, y2), conf, cls_id in zip(xyxy, confs, clses):
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        color = class_color(int(cls_id))
        label = f"{names.get(int(cls_id), str(int(cls_id)))} {conf:.2f}"

        cv2.rectangle(img_bgr, (x1, y1), (x2, y2), color, t)

        (tw, th), bl = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, fs, t)
        x_bg2 = min(x1 + tw + 6, w - 1)
        y_bg2 = y1 - th - 6
        y_bg2 = y_bg2 if y_bg2 > 5 else y1 + th + 6
        cv2.rectangle(img_bgr, (x1, y_bg2 - th - 4), (x_bg2, y_bg2), color, -1)
        ty = y_bg2 - 6 if y_bg2 > y1 else y_bg2 - th - 6
        cv2.putText(img_bgr, label, (x1 + 3, ty + th),
                    cv2.FONT_HERSHEY_SIMPLEX, fs, (0, 0, 0), t//2 + 1, cv2.LINE_AA)
    return img_bgr

def fit_to_screen(img_bgr):
    h, w = img_bgr.shape[:2]
    scale = min(MAX_DISPLAY_W / max(1, w), MAX_DISPLAY_H / max(1, h), 1.0)
    if scale < 1.0:
        img_bgr = cv2.resize(img_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return img_bgr

def main():
    if not Path(MODEL_PATH).exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
    if not Path(INPUT_DIR).exists():
        raise FileNotFoundError(f"Input folder not found: {INPUT_DIR}")

    ensure_dirs()
    imgs = list_images(INPUT_DIR)
    if not imgs:
        print(f"⚠️ No images in {INPUT_DIR}")
        return

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    start_time = time.time()
    model = YOLO(MODEL_PATH)
    print("✨ Model loaded in {:.3f}s".format(time.time() - start_time))

    idx = 0
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    # Windows arrow key codes + cross-platform fallbacks
    LEFT_KEYS  = {ord('b'), 2424832, 81}         # 'b', Left arrow (Win/Linux)
    RIGHT_KEYS = {32, 13, 2555904, 83}           # Space, Enter, Right arrow
    SAVE_KEYS  = {ord('s')}
    QUIT_KEYS  = {ord('q'), 27}                  # 'q', ESC

    while 0 <= idx < len(imgs):
        img_path = imgs[idx]
        orig = cv2.imread(img_path)
        if orig is None:
            print(f"⚠️ Could not read {img_path}, skipping.")
            idx += 1
            continue

        start_time = time.time()
        results = model.predict(
            source=orig, imgsz=IMGSZ, conf=CONF, iou=IOU, device=device, verbose=False
        )
        print(f"✨ Inference time: {time.time() - start_time:.3f}s")
        r = results[0]

        vis = orig.copy()
        vis = draw_detections(vis, r)

        caption = f"[{idx+1}/{len(imgs)}] {Path(img_path).name}  |  keys: SPACE/ENTER/→ next  •  b/← prev  •  s save  •  q/ESC quit"
        draw_caption(vis, caption)

        disp = fit_to_screen(vis)
        cv2.imshow(WINDOW_NAME, disp)

        key = cv2.waitKey(0)
        if key in QUIT_KEYS:
            break
        elif key in LEFT_KEYS:
            idx = max(0, idx - 1)
        elif key in RIGHT_KEYS:
            idx = min(len(imgs) - 1, idx + 1)
        elif key in SAVE_KEYS:
            out_path = Path(OUTPUT_DIR) / Path(img_path).name
            cv2.imwrite(str(out_path), vis)  # save full-res annotated
            print(f"💾 Saved: {out_path}")
        else:
            idx = min(len(imgs) - 1, idx + 1)

    cv2.destroyAllWindows()
    print("✅ Done.")

if __name__ == "__main__":
    main()
