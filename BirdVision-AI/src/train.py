"""
src/train.py
End-to-end training and validation engine with metric tracking,
checkpointing the best model, and plotting loss/accuracy curves.
"""

from pathlib import Path
import time
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt

from dataset import create_dataloaders
from model import BirdCNN

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
PLOTS_DIR = PROJECT_ROOT / "results" / "plots"

# Hyperparameters
NUM_EPOCHS = 15
BATCH_SIZE = 16
LEARNING_RATE = 0.0005


def train_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")
    
    # 1. Load Data
    dataloaders, class_names = create_dataloaders(DATA_DIR, batch_size=BATCH_SIZE)
    num_classes = len(class_names)
    
    # 2. Instantiate Model, Loss, Optimizer
    model = BirdCNN(num_classes=num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    # History containers for performance visualization
    history = {
        "train_loss": [], "val_loss": [],
        "train_acc": [],  "val_acc": []
    }
    
    best_val_acc = 0.0
    start_time = time.time()
    
    print("\nStarting Training Pipeline...")
    print("=" * 65)
    
    for epoch in range(1, NUM_EPOCHS + 1):
        # ----------------- TRAINING PHASE -----------------
        model.train()
        running_train_loss = 0.0
        running_train_corrects = 0
        total_train_samples = 0
        
        for images, labels in dataloaders["train"]:
            images = images.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            # Extract predicted class index
            _, preds = torch.max(outputs, 1)
            
            loss.backward()
            optimizer.step()
            
            running_train_loss += loss.item() * images.size(0)
            running_train_corrects += torch.sum(preds == labels.data).item()
            total_train_samples += images.size(0)
            
        epoch_train_loss = running_train_loss / total_train_samples
        epoch_train_acc = running_train_corrects / total_train_samples
        
        # ----------------- VALIDATION PHASE -----------------
        model.eval()
        running_val_loss = 0.0
        running_val_corrects = 0
        total_val_samples = 0
        
        with torch.no_grad():
            for images, labels in dataloaders["val"]:
                images = images.to(device)
                labels = labels.to(device)
                
                outputs = model(images)
                loss = criterion(outputs, labels)
                _, preds = torch.max(outputs, 1)
                
                running_val_loss += loss.item() * images.size(0)
                running_val_corrects += torch.sum(preds == labels.data).item()
                total_val_samples += images.size(0)
                
        epoch_val_loss = running_val_loss / total_val_samples
        epoch_val_acc = running_val_corrects / total_val_samples
        
        # Record metrics
        history["train_loss"].append(epoch_train_loss)
        history["val_loss"].append(epoch_val_loss)
        history["train_acc"].append(epoch_train_acc)
        history["val_acc"].append(epoch_val_acc)
        
        print(f"Epoch {epoch:02d}/{NUM_EPOCHS:02d} | "
              f"Train Loss: {epoch_train_loss:.4f} - Train Acc: {epoch_train_acc * 100:.1f}% | "
              f"Val Loss: {epoch_val_loss:.4f} - Val Acc: {epoch_val_acc * 100:.1f}%")
        
        # Save best model checkpoint based on validation accuracy
        if epoch_val_acc > best_val_acc:
            best_val_acc = epoch_val_acc
            save_path = MODELS_DIR / "best_custom_cnn.pth"
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_acc": best_val_acc,
                "classes": class_names
            }, save_path)
            
    elapsed = time.time() - start_time
    print("=" * 65)
    print(f"Training completed in {elapsed // 60:.0f}m {elapsed % 60:.0f}s")
    print(f"Best Validation Accuracy: {best_val_acc * 100:.2f}%\n")
    
    plot_training_curves(history)


def plot_training_curves(history):
    """Saves loss and accuracy curves to disk."""
    epochs = range(1, len(history["train_loss"]) + 1)
    
    plt.figure(figsize=(12, 5))
    
    # 1. Loss Subplot
    plt.subplot(1, 2, 1)
    plt.plot(epochs, history["train_loss"], label="Train Loss", color="#1f77b4", marker='o')
    plt.plot(epochs, history["val_loss"], label="Val Loss", color="#ff7f0e", marker='s')
    plt.title("Loss Curves per Epoch")
    plt.xlabel("Epoch")
    plt.ylabel("Cross-Entropy Loss")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    
    # 2. Accuracy Subplot
    plt.subplot(1, 2, 2)
    plt.plot(epochs, [acc * 100 for acc in history["train_acc"]], label="Train Acc", color="#1f77b4", marker='o')
    plt.plot(epochs, [acc * 100 for acc in history["val_acc"]], label="Val Acc", color="#ff7f0e", marker='s')
    plt.title("Accuracy Curves per Epoch")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy (%)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    
    plt.tight_layout()
    output_path = PLOTS_DIR / "training_curves_custom_cnn.png"
    plt.savefig(output_path, dpi=200)
    plt.close('all')
    print(f"Saved training curve figure to: {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    train_model()