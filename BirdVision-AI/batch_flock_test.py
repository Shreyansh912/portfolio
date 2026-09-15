"""
batch_flock_test.py
Runs detection across multiple test images and displays flock counts.
"""

from collections import Counter
from pathlib import Path
from ultralytics import YOLO

# 1. Dynamically locate the trained model
weights = max(Path(".").glob("**/weights/best.pt"), key=lambda p: p.stat().st_mtime)
model = YOLO(str(weights))

# 2. Grab test images
test_dir = Path("Birds-Species-1/test/images")
test_images = list(test_dir.glob("*.jpg"))[:5]

output_dir = Path("results/batch_test")
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print(f"RUNNING FLOCK DETECTION ON {len(test_images)} TEST SAMPLES")
print("=" * 60)

for img_path in test_images:
    results = model.predict(source=str(img_path), conf=0.25, verbose=False)
    res = results[0]
    
    classes = [int(box.cls[0].item()) for box in res.boxes]
    counts = Counter([res.names[c] for c in classes])
    
    print(f"\nImage: {img_path.name}")
    print(f"Total Detected: {len(classes)}")
    for name, cnt in counts.items():
        print(f"  - {name}: {cnt}")
        
    # Save visual result
    res.save(filename=str(output_dir / img_path.name))

print("\n" + "=" * 60)
print(f"Annotated batch images saved to: {output_dir}")
print("=" * 60)