"""
detect_test.py
Demonstrates multi-bird detection and automated counting using YOLO.
"""

from pathlib import Path
from ultralytics import YOLO
import cv2

# Load a lightweight, fast real-time model
model = YOLO("yolov8n.pt")

# Pass any image with multiple birds or birds in a flock
# Replace this path with an image file of your choice
image_path = "test_flock.jpg" 

if not Path(image_path).exists():
    print(f"Place an image with multiple birds at '{image_path}' to test.")
else:
    results = model(image_path)
    result = results[0]
    
    # Filter detections specifically for 'bird' (class id 14 in COCO dataset)
    bird_boxes = [box for box in result.boxes if int(box.cls[0]) == 14]
    
    print("=" * 45)
    print(f"Total Birds Detected & Counted: {len(bird_boxes)}")
    print("=" * 45)
    
    # Save the output image with drawn bounding boxes and labels
    output_path = "detected_birds.jpg"
    result.save(filename=output_path)
    print(f"Saved annotated detection to: {output_path}")