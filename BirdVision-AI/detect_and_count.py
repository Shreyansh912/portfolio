"""
detect_and_count.py
Runs the fine-tuned YOLOv8 bird detector on an image or video,
identifies individual species, and tallies total bird counts per class.
"""

from collections import Counter
from pathlib import Path
import cv2
from ultralytics import YOLO


# Search project directory for any trained weights
candidate_weights = list(Path(".").glob("**/weights/best.pt"))

if not candidate_weights:
    raise FileNotFoundError(
        "Could not find any 'best.pt' file. Verify that YOLO training completed successfully."
    )

# Pick the newest trained weights file automatically
MODEL_PATH = max(candidate_weights, key=lambda p: p.stat().st_mtime)
print(f"Loaded weights from: {MODEL_PATH}")

model = YOLO(str(MODEL_PATH))

def detect_and_count(source_path: str, conf_threshold: float = 0.25, save_annotated: bool = True):
    source = Path(source_path)
    if not source.exists():
        print(f"Error: Source file '{source_path}' does not exist.")
        return

    # 2. Run inference
    results = model.predict(source=str(source), conf=conf_threshold, save=False)
    result = results[0]

    # 3. Extract bounding boxes and predicted species classes
    class_names = result.names
    detected_classes = [int(box.cls[0].item()) for box in result.boxes]
    species_counts = Counter([class_names[c_id] for c_id in detected_classes])
    total_birds = len(detected_classes)

    # 4. Print counting summary
    print("\n" + "=" * 45)
    print(f"DETECTION & COUNT SUMMARY: {source.name}")
    print("=" * 45)
    print(f"Total Birds Detected: {total_birds}")
    print("-" * 45)
    if total_birds > 0:
        for species, count in species_counts.items():
            print(f"  • {species}: {count}")
    else:
        print("  No birds detected above the confidence threshold.")
    print("=" * 45)

    # 5. Save annotated image with bounding boxes
    if save_annotated:
        output_dir = Path("results")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"detected_{source.stem}.jpg"
        
        annotated_frame = result.plot()
        cv2.imwrite(str(output_file), annotated_frame)
        print(f"Annotated result saved to: {output_file}\n")

if __name__ == "__main__":
    # Test on an image from the test set or any custom photo/flock image
    test_images = list(Path("Birds-Species-1/test/images").glob("*.jpg"))
    sample_image = str(test_images[0]) if test_images else "test_flock.jpg"
    
    detect_and_count(sample_image, conf_threshold=0.10)