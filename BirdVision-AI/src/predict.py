"""
src/predict.py
Inference module: loads the best ResNet-18 weights, preprocesses a single image,
and returns top-K predictions with associated confidence percentages.
"""

from pathlib import Path
import torch
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "best_transfer_resnet18.pth"

# Exact ImageNet statistics used during training
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]
IMAGE_SIZE = 224

INFERENCE_TRANSFORM = transforms.Compose([
    transforms.Resize(IMAGE_SIZE),
    transforms.CenterCrop(IMAGE_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
])


class BirdPredictor:
    def __init__(self, model_path: Path = MODEL_PATH):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        if not model_path.exists():
            raise FileNotFoundError(f"Trained model not found at {model_path}")
            
        checkpoint = torch.load(model_path, map_location=self.device)
        self.class_names = checkpoint["classes"]
        num_classes = len(self.class_names)
        
        # Build matching ResNet-18 architecture
        try:
            self.model = models.resnet18(weights=None)
        except TypeError:
            self.model = models.resnet18(pretrained=False)
            
        in_features = self.model.fc.in_features
        self.model.fc = torch.nn.Sequential(
            torch.nn.Dropout(0.3),
            torch.nn.Linear(in_features, num_classes)
        )
        
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(self.device)
        self.model.eval()

    def predict(self, image_path: Path, top_k: int = 3):
        """Processes an image file and returns top-K predictions with confidence."""
        with Image.open(image_path) as img:
            rgb_img = img.convert("RGB")
            
        tensor = INFERENCE_TRANSFORM(rgb_img).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(tensor)
            probabilities = F.softmax(outputs, dim=1)[0]
            
        top_probs, top_indices = torch.topk(probabilities, k=min(top_k, len(self.class_names)))
        
        results = []
        for prob, idx in zip(top_probs, top_indices):
            results.append({
                "species": self.class_names[idx.item()],
                "confidence": prob.item() * 100
            })
            
        return results


if __name__ == "__main__":
    predictor = BirdPredictor()
    
    # Run test on a sample image from the test set
    sample_images = list((PROJECT_ROOT / "data" / "test").glob("*/*.jpg"))
    if not sample_images:
        print("No test images found to run prediction.")
    else:
        test_img = sample_images[0]
        print(f"Testing inference on: {test_img.name}")
        predictions = predictor.predict(test_img, top_k=3)
        
        print("\n" + "=" * 40)
        print("          PREDICTION RESULTS")
        print("=" * 40)
        for rank, item in enumerate(predictions, 1):
            species_clean = item['species'].replace('_', ' ').title()
            print(f"{rank}. {species_clean:<18} : {item['confidence']:.2f}%")
        print("=" * 40)