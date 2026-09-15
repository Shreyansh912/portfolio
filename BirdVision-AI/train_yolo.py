"""
train_yolo.py
Trains YOLOv8 locally on the Birds-Species-1 dataset using CUDA.
"""

from pathlib import Path
import torch
from ultralytics import YOLO

def main():
    device = 0 if torch.cuda.is_available() else "cpu"
    device_name = torch.cuda.get_device_name(0) if device == 0 else "CPU"
    print("=" * 60)
    print(f"Training on device: {device} ({device_name})")
    print("=" * 60)

    # Point directly to the downloaded Roboflow data.yaml
    yaml_path = Path("Birds-Species-1/data.yaml").resolve()
    
    if not yaml_path.exists():
        raise FileNotFoundError(f"Cannot find {yaml_path}. Check folder name.")

    print(f"Dataset config: {yaml_path}")

    # Load pretrained YOLOv8 Nano backbone
    model = YOLO("yolov8n.pt")

    # Fine-tune the detector
    model.train(
        data=str(yaml_path),
        epochs=30,
        imgsz=640,
        batch=16,
        device=device,
        workers=2,
        project="models",
        name="yolov8_birds_detector",
        exist_ok=True,
        plots=True
    )

    print("=" * 60)
    print("Training finished!")
    print("Best weights: models/yolov8_birds_detector/weights/best.pt")
    print("=" * 60)

if __name__ == "__main__":
    main()