"""
src/model.py
Defines the baseline Custom CNN architecture for bird species classification.
"""

import torch
import torch.nn as nn


class BirdCNN(nn.Module):
    def __init__(self, num_classes: int = 5):
        super(BirdCNN, self).__init__()
        
        # Feature Extractor (Convolutional Backbone)
        self.features = nn.Sequential(
            # Block 1: Input (3, 224, 224) -> Output (16, 112, 112)
            nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # Block 2: Input (16, 112, 112) -> Output (32, 56, 56)
            nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # Block 3: Input (32, 56, 56) -> Output (64, 28, 28)
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        
        # Classifier Head (Fully Connected Layers)
        # Spatial dimensions at end of conv blocks: 64 channels * 28 height * 28 width = 50,176
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 28 * 28, 128),
            nn.ReLU(),
            nn.Dropout(p=0.5),
            nn.Linear(128, num_classes)  # Outputs 5 raw logits
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        logits = self.classifier(x)
        return logits


if __name__ == "__main__":
    # Diagnostic test: pass a dummy batch through the model and verify parameter counts
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Instantiating model on device: {device}")
    
    model = BirdCNN(num_classes=5).to(device)
    
    # Generate a dummy batch matching our DataLoader output: [Batch=16, Channels=3, H=224, W=224]
    dummy_input = torch.randn(16, 3, 224, 224, device=device)
    
    # Forward pass
    output_logits = model(dummy_input)
    
    print("\n--- Model Dimensional Validation ---")
    print(f"Input Shape:        {dummy_input.shape}")
    print(f"Output Logit Shape: {output_logits.shape}")
    
    # Count total trainable parameters
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Trainable Params:   {total_params:,}")
    print("=" * 45)
    print("Model architecture compiled and validated successfully!")