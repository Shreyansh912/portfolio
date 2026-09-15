"""
two_stage_pipeline.py (Optimized)
"""

from collections import Counter
from pathlib import Path
import cv2
from PIL import Image
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from ultralytics import YOLO

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 1. Detector
detector = YOLO("yolov8n.pt")

# 2. Classifier
classifier_weights = Path("models/best_transfer_resnet18.pth")
checkpoint = torch.load(classifier_weights, map_location=device)

if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
    state_dict = checkpoint["model_state_dict"]
    CLASS_NAMES = checkpoint.get("classes", [])
else:
    state_dict = checkpoint
    CLASS_NAMES = ['american_robin', 'bald_eagle', 'blue_jay', 'house_sparrow', 'mallard']

classifier = models.resnet18(weights=None)
num_features = classifier.fc.in_features

if "fc.1.weight" in state_dict:
    classifier.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(num_features, len(CLASS_NAMES))
    )
else:
    classifier.fc = nn.Linear(num_features, len(CLASS_NAMES))

classifier.load_state_dict(state_dict)
classifier.to(device)
classifier.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


def process_image(image_path: str, det_conf: float = 0.25, clf_conf: float = 0.50):
    img_bgr = cv2.imread(str(image_path))
    if img_bgr is None:
        print(f"Could not read image: {image_path}")
        return

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    h, w, _ = img_bgr.shape

    # Stage 1: Detect
    results = detector.predict(source=img_rgb, conf=det_conf, verbose=False)[0]
    bird_boxes = [box for box in results.boxes if int(box.cls[0].item()) == 14]

    detected_species = []

    # Stage 2: Classify with 10% padding
    for box in bird_boxes:
        xyxy = box.xyxy[0].cpu().numpy().astype(int)
        bw = xyxy[2] - xyxy[0]
        bh = xyxy[3] - xyxy[1]
        
        # Add slight margin around bird
        pad_x, pad_y = int(bw * 0.1), int(bh * 0.1)
        x1 = max(0, xyxy[0] - pad_x)
        y1 = max(0, xyxy[1] - pad_y)
        x2 = min(w, xyxy[2] + pad_x)
        y2 = min(h, xyxy[3] + pad_y)

        crop = img_rgb[y1:y2, x1:x2]
        if crop.size == 0:
            continue

        pil_crop = Image.fromarray(crop)
        tensor_crop = transform(pil_crop).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = classifier(tensor_crop)
            probs = torch.softmax(outputs, dim=1)
            top_prob, pred_idx = torch.max(probs, dim=1)
            
            score = top_prob.item()
            if score >= clf_conf:
                species_name = CLASS_NAMES[pred_idx.item()]
                label = f"{species_name} {score*100:.1f}%"
            else:
                species_name = "unknown_bird"
                label = f"unknown ({score*100:.1f}%)"

        detected_species.append(species_name)

        # Draw box and tag
        cv2.rectangle(img_bgr, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (0, 255, 0), 2)
        cv2.putText(img_bgr, label, (xyxy[0], max(20, xyxy[1] - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

    counts = Counter(detected_species)
    print("\n" + "=" * 45)
    print(f"PIPELINE SUMMARY: {Path(image_path).name}")
    print("=" * 45)
    print(f"Total Birds Detected: {len(detected_species)}")
    for sp, cnt in counts.items():
        print(f"  • {sp}: {cnt}")
    print("=" * 45)

    output_dir = Path("results/pipeline_output")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"result_{Path(image_path).name}"
    cv2.imwrite(str(out_path), img_bgr)
    print(f"Saved visualization to: {out_path}\n")


if __name__ == "__main__":
    test_samples = list(Path("data/test").glob("**/*.jpg"))
    sample = str(test_samples[0]) if test_samples else "test_flock.jpg"
    process_image(sample)