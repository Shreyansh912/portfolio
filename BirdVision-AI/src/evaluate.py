"""
src/evaluate.py
Loads the best trained checkpoint, computes classification metrics
on the held-out test split, and generates a Confusion Matrix.
"""

from pathlib import Path
import torch
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix

from dataset import create_dataloaders
from model import BirdCNN

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "results" / "confusion_matrix"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def evaluate_test_set():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Running evaluation on: {device}")
    
    # 1. Load DataLoaders
    dataloaders, class_names = create_dataloaders(DATA_DIR, batch_size=16)
    test_loader = dataloaders["test"]
    
    # 2. Re-instantiate Architecture & Load Saved Checkpoint
    checkpoint_path = MODELS_DIR / "best_custom_cnn.pth"
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found at {checkpoint_path}. Train model first!")
        
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    model = BirdCNN(num_classes=len(class_names)).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    
    print(f"Loaded checkpoint saved from epoch {checkpoint['epoch']} with Val Acc: {checkpoint['val_acc']*100:.2f}%")
    
    all_preds = []
    all_targets = []
    
    # 3. Inference loop without gradient tracking
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(labels.numpy())
            
    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)
    
    # 4. Classification Metrics Report
    print("\n" + "=" * 60)
    print("           TEST SET CLASSIFICATION REPORT")
    print("=" * 60)
    report = classification_report(
        all_targets, 
        all_preds, 
        target_names=class_names, 
        digits=4
    )
    print(report)
    
    # 5. Confusion Matrix Computation & Visualization
    cm = confusion_matrix(all_targets, all_preds)
    plot_confusion_matrix(cm, class_names)


def plot_confusion_matrix(cm, class_names):
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    
    tick_marks = np.arange(len(class_names))
    ax.set_xticks(tick_marks)
    ax.set_yticks(tick_marks)
    ax.set_xticklabels(class_names, rotation=45, ha="right", fontsize=10)
    ax.set_yticklabels(class_names, fontsize=10)
    
    # Annotate counts inside matrix cells
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], 'd'),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black",
                    fontweight="bold")
            
    ax.set_ylabel('True Species Label', fontweight="bold")
    ax.set_xlabel('Predicted Species Label', fontweight="bold")
    ax.set_title('Custom CNN Confusion Matrix (Test Set)', pad=15, fontweight="bold")
    plt.tight_layout()
    
    save_file = RESULTS_DIR / "confusion_matrix_custom_cnn.png"
    plt.savefig(save_file, dpi=200)
    plt.close('all')
    print(f"Saved confusion matrix plot to: {save_file.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    evaluate_test_set()