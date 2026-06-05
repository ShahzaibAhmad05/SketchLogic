from ultralytics.models import YOLO


def main():
    model = YOLO("yolov8n-obb.pt")
    model.train(
        project="runs/train",
        name="run",
        data="data/config.yaml",
        epochs=100,
        imgsz=1024,
        optimizer="AdamW",
        cos_lr=True,
        plots=True
    )


if __name__ == "__main__":
    main()
