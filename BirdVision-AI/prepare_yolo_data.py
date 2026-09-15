"""
prepare_yolo_data.py
Converts our existing 5-species dataset into YOLO detection format:
1. Runs pretrained YOLO to locate bird bounding boxes in each image.
2. Formats coordinates to YOLO standard (class_id x_center y_center width height).
3. Structures files into datasets/bird_detection/.
4. Generates data.yaml automatically.
"""

from pathlib import Path
import shutil
import cv2
from ultralytics import YOLO

ROOT_DIR = Path(__file__).resolve().parent
SOURCE_DATA = ROOT_DIR / "data"
YOLO_ROOT = ROOT_DIR / "datasets" / "bird_detection"

# Map folder names to detection class IDs
CLASS_MAP = {
    "american_robin": 0,
    "bald_eagle": 1,
    "blue_jay": 2,
    "house_sparrow": 3,
    "mallard": 4
}


def prepare_dataset():
    # 1. Initialize YOLO detector to extract bird boxes
    detector = YOLO("yolov8n.pt")
    
    # 2. Create target YOLO directories
    for split in ["train", "val"]:
        (YOLO_ROOT / "images" / split).mkdir(parents=True, exist_ok=True)
        (YOLO_ROOT / "labels" / split).mkdir(parents=True, exist_ok=True)

    print("Converting classification dataset to YOLO bounding-box format...")
    print("=" * 65)

    total_annotated = 0

    for split in ["train", "val"]:
        split_dir = SOURCE_DATA / split
        if not split_dir.exists():
            continue

        for species_folder in split_dir.iterdir():
            if not species_folder.is_dir() or species_folder.name not in CLASS_MAP:
                continue

            class_id = CLASS_MAP[species_folder.name]
            image_files = list(species_folder.glob("*.jpg")) + list(species_folder.glob("*.png"))

            for img_path in image_files:
                # Detect bird presence
                results = detector(str(img_path), verbose=False)[0]
                
                # Filter COCO class 14 ('bird') with confidence > 0.3
                boxes = [
                    box for box in results.boxes 
                    if int(box.cls[0]) == 14 and float(box.conf[0]) > 0.3
                ]
                
                dest_img_path = YOLO_ROOT / "images" / split / img_path.name
                dest_lbl_path = YOLO_ROOT / "labels" / split / f"{img_path.stem}.txt"

                shutil.copy(img_path, dest_img_path)

                lines = []
                if len(boxes) > 0:
                    for b in boxes:
                        # YOLO format: normalized [x_center, y_center, width, height]
                        xywhn = b.xywhn[0].tolist()
                        lines.append(f"{class_id} {xywhn[0]:.6f} {xywhn[1]:.6f} {xywhn[2]:.6f} {xywhn[3]:.6f}")
                else:
                    # Fallback if uncropped: full image bounding box
                    lines.append(f"{class_id} 0.500000 0.500000 0.900000 0.900000")

                with open(dest_lbl_path, "w") as f:
                    f.write("\n".join(lines))

                total_annotated += 1

    # 3. Auto-generate data.yaml
    yaml_content = f"""path: {YOLO_ROOT.as_posix()}
train: images/train
val: images/val

names:
  0: american_robin
  1: bald_eagle
  2: blue_jay
  3: house_sparrow
  4: mallard
"""
    yaml_path = YOLO_ROOT / "data.yaml"
    with open(yaml_path, "w") as f:
        f.write(yaml_content)

    print("=" * 65)
    print(f"Processed {total_annotated} images with bounding box annotations.")
    print(f"Generated YAML configuration at: {yaml_path}")


if __name__ == "__main__":
    prepare_dataset()