"""
src/error_analysis.py
Identifies misclassified images from the test split, displays the top
errors with true vs predicted labels and confidence scores, and saves a visual grid.
"""

from pathlib import Path
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
from PIL import Image

from dataset import create_dataloaders
from model import BirdCNN

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "results" / "plots"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def get_image_path(dataset, idx: int):
    """Safely retrieves the image file path from an ImageFolder dataset."""
    if hasattr(dataset, "samples") and len(dataset.samples) > idx:
        return dataset.samples[idx][0]
    if hasattr(dataset, "imgs") and len(dataset.imgs) > idx:
        return dataset.imgs[idx][0]
    # Fallback: scan test directory deterministically
    all_files = sorted(list((DATA_DIR / "test").glob("*/*.jpg")))
    return str(all_files[idx])


def analyze_errors():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 1. Load Data and Checkpoint
    dataloaders, class_names = create_dataloaders(DATA_DIR, batch_size=1)
    test_dataset = dataloaders["test"].dataset
    
    checkpoint_path = MODELS_DIR / "best_custom_cnn.pth"
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found at {checkpoint_path}")
        
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    model = BirdCNN(num_classes=len(class_names)).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    
    misclassified = []
    
    print("Running error inspection on test set...")
    print("=" * 65)
    
    with torch.no_grad():
        for idx in range(len(test_dataset)):
            img_tensor, label = test_dataset[idx]
            img_tensor_batch = img_tensor.unsqueeze(0).to(device)
            output = model(img_tensor_batch)
            
            # Convert raw logits to probabilities
            probabilities = F.softmax(output, dim=1)[0]
            confidence, pred_idx = torch.max(probabilities, dim=0)
            
            pred_label = pred_idx.item()
            true_label = label
            
            if pred_label != true_label:
                img_path = get_image_path(test_dataset, idx)
                misclassified.append({
                    "path": img_path,
                    "true": class_names[true_label],
                    "pred": class_names[pred_label],
                    "confidence": confidence.item() * 100
                })
                
    print(f"Total misclassifications found: {len(misclassified)} / {len(test_dataset)}")
    print("-" * 65)
    
    # Sort by prediction confidence descending
    misclassified_sorted = sorted(misclassified, key=lambda x: x["confidence"], reverse=True)
    
    for i, item in enumerate(misclassified_sorted[:6]):
        print(f"[{i+1}] File: {Path(item['path']).name}")
        print(f"    True: {item['true']:<15} | Predicted: {item['pred']:<15} | Confidence: {item['confidence']:.2f}%")
        
    # Visualize top 4 misclassified images
    plot_errors(misclassified_sorted[:4])


def plot_errors(error_list):
    if not error_list:
        return
        
    fig, axes = plt.subplots(1, len(error_list), figsize=(14, 4))
    if len(error_list) == 1:
        axes = [axes]
        
    for ax, item in zip(axes, error_list):
        img = Image.open(item["path"]).convert("RGB")
        ax.imshow(img)
        title = f"True: {item['true']}\nPred: {item['pred']}\nConf: {item['confidence']:.1f}%"
        ax.set_title(title, fontsize=9, color="red")
        ax.axis("off")
        
    plt.tight_layout()
    save_path = RESULTS_DIR / "error_analysis_samples.png"
    plt.savefig(save_path, dpi=200)
    plt.close('all')
    print("-" * 65)
    print(f"Saved misclassified sample figure to: {save_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    analyze_errors()