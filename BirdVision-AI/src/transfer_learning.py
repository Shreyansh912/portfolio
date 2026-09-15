"""
src/transfer_learning.py
Implements Transfer Learning using ResNet-18 pretrained on ImageNet.
Freezes the feature backbone, replaces the classifier head, trains on our
5 bird species, and evaluates against the held-out test split.
"""

from pathlib import Path
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import numpy as np

from dataset import create_dataloaders

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
PLOTS_DIR = PROJECT_ROOT / "results" / "plots"
RESULTS_DIR = PROJECT_ROOT / "results" / "confusion_matrix"

NUM_EPOCHS = 10
BATCH_SIZE = 16
LEARNING_RATE = 0.001


def build_transfer_model(num_classes: int):
    # 1. Load Pretrained ResNet-18
    # Using modern weights parameter with fallback for legacy torchvision
    try:
        weights = models.ResNet18_Weights.DEFAULT
        model = models.resnet18(weights=weights)
    except AttributeError:
        model = models.resnet18(pretrained=True)
        
    # 2. Freeze all convolutional backbone layers
    for param in model.parameters():
        param.requires_grad = False
        
    # 3. Replace the final classification head
    # ResNet-18 fc input feature dimension is 512
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, num_classes)
    )
    
    return model


def train_and_evaluate_transfer():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Transfer Learning running on: {device}")
    
    dataloaders, class_names = create_dataloaders(DATA_DIR, batch_size=BATCH_SIZE)
    num_classes = len(class_names)
    
    model = build_transfer_model(num_classes).to(device)
    
    # Train ONLY the parameters of the newly attached head
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    print(f"Total Model Parameters:     {sum(p.numel() for p in model.parameters()):,}")
    print(f"Trainable Parameters (Head): {sum(p.numel() for p in trainable_params):,}")
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(trainable_params, lr=LEARNING_RATE)
    
    best_val_acc = 0.0
    start_time = time.time()
    
    print("\nStarting ResNet-18 Transfer Learning...")
    print("=" * 65)
    
    for epoch in range(1, NUM_EPOCHS + 1):
        # --- TRAIN PHASE ---
        model.train()
        running_loss, running_corrects, total_samples = 0.0, 0, 0
        
        for images, labels in dataloaders["train"]:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            _, preds = torch.max(outputs, 1)
            
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * images.size(0)
            running_corrects += torch.sum(preds == labels.data).item()
            total_samples += images.size(0)
            
        epoch_train_loss = running_loss / total_samples
        epoch_train_acc = running_corrects / total_samples
        
        # --- VAL PHASE ---
        model.eval()
        val_loss, val_corrects, val_samples = 0.0, 0, 0
        
        with torch.no_grad():
            for images, labels in dataloaders["val"]:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                _, preds = torch.max(outputs, 1)
                
                val_loss += loss.item() * images.size(0)
                val_corrects += torch.sum(preds == labels.data).item()
                val_samples += images.size(0)
                
        epoch_val_loss = val_loss / val_samples
        epoch_val_acc = val_corrects / val_samples
        
        print(f"Epoch {epoch:02d}/{NUM_EPOCHS:02d} | "
              f"Train Loss: {epoch_train_loss:.4f} - Train Acc: {epoch_train_acc*100:.1f}% | "
              f"Val Loss: {epoch_val_loss:.4f} - Val Acc: {epoch_val_acc*100:.1f}%")
        
        if epoch_val_acc > best_val_acc:
            best_val_acc = epoch_val_acc
            save_path = MODELS_DIR / "best_transfer_resnet18.pth"
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "val_acc": best_val_acc,
                "classes": class_names
            }, save_path)
            
    print("=" * 65)
    print(f"Transfer Learning training finished in {time.time() - start_time:.1f}s")
    print(f"Best Validation Accuracy: {best_val_acc*100:.2f}%\n")
    
    # --- FINAL TEST EVALUATION ---
    evaluate_transfer_on_test(model, dataloaders["test"], class_names, device)


def evaluate_transfer_on_test(model, test_loader, class_names, device):
    print("Evaluating ResNet-18 on Held-Out Test Set...")
    checkpoint = torch.load(MODELS_DIR / "best_transfer_resnet18.pth", map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    
    all_preds = []
    all_targets = []
    
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(labels.numpy())
            
    print("\n" + "=" * 60)
    print("        RESNET-18 TEST SET CLASSIFICATION REPORT")
    print("=" * 60)
    print(classification_report(all_targets, all_preds, target_names=class_names, digits=4))
    
    cm = confusion_matrix(all_targets, all_preds)
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Greens)
    ax.figure.colorbar(im, ax=ax)
    
    tick_marks = np.arange(len(class_names))
    ax.set_xticks(tick_marks)
    ax.set_yticks(tick_marks)
    ax.set_xticklabels(class_names, rotation=45, ha="right")
    ax.set_yticklabels(class_names)
    
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], 'd'),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black",
                    fontweight="bold")
            
    ax.set_ylabel('True Label', fontweight="bold")
    ax.set_xlabel('Predicted Label', fontweight="bold")
    ax.set_title('ResNet-18 Confusion Matrix (Test Set)', pad=15, fontweight="bold")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "confusion_matrix_resnet18.png", dpi=200)
    plt.close('all')


if __name__ == "__main__":
    train_and_evaluate_transfer()