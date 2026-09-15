"""
src/pipeline.py
Production Two-Stage Bird Detection & Classification Pipeline.
"""

from collections import Counter
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from ultralytics import YOLO

class BirdVisionPipeline:
    def __init__(self, model_path: str = "models/best_transfer_resnet18.pth"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.detector = YOLO("yolov8n.pt")
        
        # Load classifier checkpoint
        ckpt_path = Path(model_path)
        if not ckpt_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}")
            
        checkpoint = torch.load(ckpt_path, map_location=self.device)
        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]
            self.classes = checkpoint.get("classes", [
                "american_robin", "bald_eagle", "blue_jay", "house_sparrow", "mallard"
            ])
        else:
            state_dict = checkpoint
            self.classes = ["american_robin", "bald_eagle", "blue_jay", "house_sparrow", "mallard"]

        # Build ResNet-18 head
        self.classifier = models.resnet18(weights=None)
        in_feats = self.classifier.fc.in_features
        if "fc.1.weight" in state_dict:
            self.classifier.fc = nn.Sequential(
                nn.Dropout(0.3),
                nn.Linear(in_feats, len(self.classes))
            )
        else:
            self.classifier.fc = nn.Linear(in_feats, len(self.classes))
            
        self.classifier.load_state_dict(state_dict)
        self.classifier.to(self.device)
        self.classifier.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def predict(self, image_input, det_conf=0.25, clf_conf=0.50):
        """
        Accepts a file path, PIL Image, or NumPy array.
        Supports numerical values or 'auto' for dynamic thresholding.
        Returns: annotated_image (BGR np.ndarray), summary (dict), detections (list)
        """
        if isinstance(image_input, (str, Path)):
            img_bgr = cv2.imread(str(image_input))
        elif isinstance(image_input, Image.Image):
            img_bgr = cv2.cvtColor(np.array(image_input), cv2.COLOR_RGB2BGR)
        elif isinstance(image_input, np.ndarray):
            img_bgr = image_input.copy()
        else:
            raise ValueError("Unsupported image input format")

        h, w, _ = img_bgr.shape
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

       # Stage 1: Detect with calibrated threshold and IoU
        yolo_thresh = 0.25 if det_conf == "auto" else float(det_conf)
        results = self.detector.predict(
            source=img_rgb, 
            conf=yolo_thresh, 
            iou=0.45,
            imgsz=1024,
            verbose=False
        )[0]

        # Extract initial bird boxes (class 14)
        raw_boxes = []
        for box in results.boxes:
            if int(box.cls[0].item()) == 14:
                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                bw = xyxy[2] - xyxy[0]
                bh = xyxy[3] - xyxy[1]
                aspect_ratio = bh / max(bw, 1)
                if bw >= 20 and bh >= 20 and aspect_ratio < 4.5:
                    raw_boxes.append((box, xyxy))

        # Suppress nested/contained sub-boxes (e.g. head detected inside body)
        bird_boxes = []
        for i, (box_a, xyxy_a) in enumerate(raw_boxes):
            is_contained = False
            area_a = (xyxy_a[2] - xyxy_a[0]) * (xyxy_a[3] - xyxy_a[1])

            for j, (box_b, xyxy_b) in enumerate(raw_boxes):
                if i == j:
                    continue
                area_b = (xyxy_b[2] - xyxy_b[0]) * (xyxy_b[3] - xyxy_b[1])

                # Check if box_a is smaller than box_b and significantly inside box_b
                if area_a < area_b:
                    inter_x1 = max(xyxy_a[0], xyxy_b[0])
                    inter_y1 = max(xyxy_a[1], xyxy_b[1])
                    inter_x2 = min(xyxy_a[2], xyxy_b[2])
                    inter_y2 = min(xyxy_a[3], xyxy_b[3])

                    inter_w = max(0, inter_x2 - inter_x1)
                    inter_h = max(0, inter_y2 - inter_y1)
                    inter_area = inter_w * inter_h

                    # If >65% of the smaller box is inside the larger box, suppress it
                    if (inter_area / max(area_a, 1)) > 0.65:
                        is_contained = True
                        break

            if not is_contained:
                bird_boxes.append(box_a)
        for box in results.boxes:
            if int(box.cls[0].item()) == 14:
                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                bw = xyxy[2] - xyxy[0]
                bh = xyxy[3] - xyxy[1]
                aspect_ratio = bh / max(bw, 1)

                # Relaxed thresholds to catch small cutouts while dropping narrow slivers
                if bw >= 12 and bh >= 12 and aspect_ratio < 4.5:
                    bird_boxes.append(box)

        # Initialize tracking containers
        detections = []
        species_list = []

        # Stage 2: Classify
        for box in bird_boxes:
            xyxy = box.xyxy[0].cpu().numpy().astype(int)
            bw, bh = xyxy[2] - xyxy[0], xyxy[3] - xyxy[1]

            # Crop padding (10%)
            px, py = int(bw * 0.1), int(bh * 0.1)
            x1, y1 = max(0, xyxy[0] - px), max(0, xyxy[1] - py)
            x2, y2 = min(w, xyxy[2] + px), min(h, xyxy[3] + py)

            crop = img_rgb[y1:y2, x1:x2]
            if crop.size == 0:
                continue

            pil_crop = Image.fromarray(crop)
            tensor_crop = self.transform(pil_crop).unsqueeze(0).to(self.device)

            with torch.no_grad():
                out = self.classifier(tensor_crop)
                probs = torch.softmax(out, dim=1)

                top_probs, top_indices = torch.topk(probs, k=min(2, len(self.classes)), dim=1)
                p1 = top_probs[0][0].item()
                p2 = top_probs[0][1].item() if top_probs.shape[1] > 1 else 0.0
                margin = p1 - p2

            # Decision rule
            if clf_conf == "auto":
                is_confident = (p1 >= 0.50) and (margin >= 0.12)
            else:
                is_confident = (p1 >= float(clf_conf))

            if is_confident:
                species = self.classes[top_indices[0][0].item()]
                label = f"{species} {p1*100:.1f}%"
                score = p1
            else:
                species = "unknown_bird"
                label = f"unknown ({p1*100:.1f}%)"
                score = p1

            species_list.append(species)
            detections.append({
                "species": species,
                "confidence": round(score, 4),
                "box": [int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])]
            })

            # Annotate
            cv2.rectangle(img_bgr, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (0, 220, 0), 2)
            cv2.putText(img_bgr, label, (xyxy[0], max(20, xyxy[1] - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 220, 0), 1)

        summary = {
            "total_count": len(species_list),
            "species_breakdown": dict(Counter(species_list))
        }

        return img_bgr, summary, detections