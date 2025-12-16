"""
Main inference file for the model. Infers and returns the results in
a readable json format

"""

from ultralytics import YOLO
from pathlib import Path
import torch
import numpy as np


class SketchLogic():
    def __init__(self, model_path: Path) -> None:
        """ 
        Initialize the SketchLogic model.

        Args:
            model_path (Path): Path to the model file
            debug (bool, optional): Print debug info. Defaults to False.
        """

        # CONFIGURATION 
        self.MODEL_PATH = model_path

        self.IMGSZ = 1024
        self.CONF  = 0.25
        self.IOU   = 0.70

        self.MAX_DISPLAY_W = 1600
        self.MAX_DISPLAY_H = 1000

        # PATH VALIDATION CHECKS
        if not self.MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found: {self.MODEL_PATH}"
                                    "- Please run the download script to download the model."
                                    "- See the README for more information.")

        # MODEL INITIALIZATION
        self.model = YOLO(self.MODEL_PATH)

    def infer(self, img: np.ndarray) -> dict:
        """ 
        Does Inference on a single image file.
        
        Args:
            file_path (str): Path to the image file
            debug (bool, optional): Print debug info. Defaults to False.

        Returns:
            dict: A dictionary containing the inference results
        """

        # Use GPU if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # Validation checks
        if img is None:
            raise FileNotFoundError(f"Cannot infer, invalid Image.")

        # Inference
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
        boxes = xyxy

        annotations = []      # list to hold the annotations (results)
        for i, (x1, y1, x2, y2) in enumerate(boxes, start=1):
            x1, y1, x2, y2 = map(float, (x1, y1, x2, y2))
            annotations.append({
                "id": i,
                "type": str(names.get(int(clss[i-1]), int(clss[i-1])) if len(clss) >= i else ""),
                "x": int(round(x1)),
                "y": int(round(y1)),
                "width": int(round(x2 - x1)),
                "height": int(round(y2 - y1)),
                "rotation": 0
            })

        return annotations
