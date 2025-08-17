from ultralytics import YOLO
import cv2
import os
from pathlib import Path
import torch
import glob
import numpy as np
import time

class SketchLogic():
    def __init__(self, model_path: Path) -> None:
        """ Initialize the SketchLogic model

        Args:
            model_path (Path): Path to the model file
            debug (bool, optional): Print debug info. Defaults to False.
        """

        # CONFIGURATION 
        self.MODEL_PATH = model_path

        self.IMGSZ = 1024
        self.CONF  = 0.25
        self.IOU   = 0.70
        self.WINDOW_NAME = "SketchLogic Detections"

        self.MAX_DISPLAY_W = 1600
        self.MAX_DISPLAY_H = 1000

        # PATH VALIDATION CHECKS
        if not self.MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found: {self.MODEL_PATH}"
                                    "- Please run the download script to download the model."
                                    "- See the README for more information.")

        # MODEL INITIALIZATION
        start_time = time.time()
        self.model = YOLO(self.MODEL_PATH)

    @staticmethod
    def list_images(folder):
        exts = ("*.jpg","*.jpeg","*.png","*.bmp","*.tif","*.tiff","*.webp")
        files = []
        for e in exts:
            files += glob.glob(str(Path(folder) / e))
        return sorted(files)

    @staticmethod
    def class_color(cls_id: int):
        # stable pseudo-color per class (HSV->BGR)
        h = (cls_id * 0.61803398875) % 1.0
        s, v = 0.6, 1.0
        hsv = np.uint8([[[int(h*179), int(s*255), int(v*255)]]])
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0,0]
        return int(bgr[0]), int(bgr[1]), int(bgr[2])

    @staticmethod
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

    @staticmethod
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
            color = SketchLogic.class_color(int(cls_id))
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

    def fit_to_screen(self, img_bgr):
        h, w = img_bgr.shape[:2]
        scale = min(self.MAX_DISPLAY_W / max(1, w), self.MAX_DISPLAY_H / max(1, h), 1.0)
        if scale < 1.0:
            img_bgr = cv2.resize(img_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        return img_bgr

    def infer(self, file_path: str) -> dict:
        """ Does Inference on a single image file 
        
        Args:
            file_path (str): Path to the image file
            debug (bool, optional): Print debug info. Defaults to False.

        Returns:
            dict: A dictionary containing the inference results
        """

        # Use GPU if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Validation checks
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Could not find file: {file_path}")
        img = cv2.imread(str(file_path))
        if img is None:
            raise FileNotFoundError(f"Could not read image: {file_path}")

        # Inference
        start_time = time.time()
        r = self.model.predict(
            source=img, imgsz=self.IMGSZ, conf=self.CONF, iou=self.IOU,
            device=device, verbose=False, agnostic_nms=True
        )[0]

        # Load results
        boxes = r.boxes
        if boxes is not None and len(boxes):
            xyxy = boxes.xyxy.detach().cpu().numpy()         # (N,4)
            clss = boxes.cls.detach().cpu().numpy().astype(int)  # (N,)
        else:
            xyxy = np.empty((0, 4), dtype=float)
            clss = np.empty((0,), dtype=int)
        names = getattr(r, "names", getattr(self.model, "names", {}))

        return {
            "filename": Path(file_path).name,
            "path": str(file_path),
            "boxes": xyxy,          # numpy (N,4) in xyxy
            "classes": clss,        # numpy (N,)
            "names": names          # id->label dict if available
        }

    def visualize(self, result, exit_key='q', save_path=None, window_name='Detections') -> None:
        """ Visualize the results using openCV
        
        Args:
            result (dict): A dictionary containing the inference results
            exit_key (str, optional): Key to exit the visualization. Defaults to 'q'.
            save_path (str, optional): Path to save the rendered image. Defaults to None.
            window_name (str, optional): Name of the window. Defaults to 'Detections'.
        """

        img = cv2.imread(result["path"])
        if img is None:
            raise FileNotFoundError(f"Could not read image: {result['path']}")

        vis = img.copy()
        boxes, clss, names = result["boxes"], result["classes"], result.get("names", {})

        # Draw boxes + labels
        for i, (x1, y1, x2, y2) in enumerate(boxes):
            x1, y1, x2, y2 = map(int, map(round, (x1, y1, x2, y2)))
            label = str(names.get(int(clss[i]), int(clss[i]))) if len(clss) > i else ""
            cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 0), 2)
            if label:
                cv2.putText(vis, label, (x1, max(0, y1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

        # Save rendered image if requested
        if save_path:
            p = Path(save_path)
            if p.suffix:  # looks like a file path
                p.parent.mkdir(parents=True, exist_ok=True)
                out_path = p
            else:         # treat as folder
                p.mkdir(parents=True, exist_ok=True)
                out_path = p / result["filename"]
            cv2.imwrite(str(out_path))

        # Show until exit key is pressed
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.imshow(window_name, vis)

        # Normalize exit_key (e.g., 'q', 'esc', 27, etc.)
        if isinstance(exit_key, str):
            key_target = 27 if exit_key.lower() in ("esc", "escape") else ord(exit_key[0])
        else:
            key_target = int(exit_key)

        while True:
            k = cv2.waitKey(0) & 0xFFFF
            if k == key_target:
                cv2.destroyWindow(window_name)
                break
            elif cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break
            time.sleep(0.025)

    def format_results(self, result) -> dict:
        """ Get the inference results in a JSON format
        
        Args:
            result (dict): A dictionary containing the inference results

        Returns:
            dict: A dictionary containing the formatted results
        """
        
        boxes, clss, names = result["boxes"], result["classes"], result.get("names", {})

        record = {
            "filename": result["filename"],
            "annotations": []
        }
        for i, (x1, y1, x2, y2) in enumerate(boxes, start=1):
            x1, y1, x2, y2 = map(float, (x1, y1, x2, y2))
            record["annotations"].append({
                "id": i,
                "type": str(names.get(int(clss[i-1]), int(clss[i-1])) if len(clss) >= i else ""),
                "x": int(round(x1)),
                "y": int(round(y1)),
                "width": int(round(x2 - x1)),
                "height": int(round(y2 - y1)),
                "rotation": 0
            })

        return record

def main() -> None:
    """ Test Driver """
    model_path = Path("skelo_ai/SKELOv1.pt")
    image_path = Path("example.jpg")

    model = SketchLogic(model_path)  # debug=True to print debug info
    results = model.infer(image_path)

    model.visualize(results)
    # Get the results in json format
    formatted_results = model.format_results(results)
    print(formatted_results)

if __name__ == "__main__":
    main()
