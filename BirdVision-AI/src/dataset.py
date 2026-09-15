"""
src/dataset.py
Defines image transformations, loads datasets, and creates PyTorch DataLoaders.
Guarantees uniform (3, 224, 224) tensor shapes across all images.
"""

import collections
import collections.abc
from pathlib import Path
import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# Compatibility patch for collections.Iterable on modern Python
if not hasattr(collections, "Iterable"):
    collections.Iterable = collections.abc.Iterable

# Standard ImageNet statistics per channel
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

IMAGE_SIZE = 224
BATCH_SIZE = 16


def get_data_transforms():
    """
    Transforms resize and crop images to guarantee exact (224, 224) dimensions.
    """
    return {
        "train": transforms.Compose([
            transforms.Resize(IMAGE_SIZE),
            transforms.CenterCrop(IMAGE_SIZE),               # Guarantees strictly 224x224
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.1, contrast=0.1),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
        ]),
        "eval": transforms.Compose([
            transforms.Resize(IMAGE_SIZE),
            transforms.CenterCrop(IMAGE_SIZE),               # Guarantees strictly 224x224
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
        ])
    }


def create_dataloaders(data_dir: Path, batch_size: int = BATCH_SIZE):
    """
    Creates PyTorch ImageFolder datasets and DataLoaders for train, val, and test splits.
    """
    transforms_dict = get_data_transforms()
    
    image_datasets = {
        "train": datasets.ImageFolder(data_dir / "train", transform=transforms_dict["train"]),
        "val":   datasets.ImageFolder(data_dir / "val",   transform=transforms_dict["eval"]),
        "test":  datasets.ImageFolder(data_dir / "test",  transform=transforms_dict["eval"])
    }
    
    dataloaders = {
        "train": DataLoader(image_datasets["train"], batch_size=batch_size, shuffle=True,  num_workers=0),
        "val":   DataLoader(image_datasets["val"],   batch_size=batch_size, shuffle=False, num_workers=0),
        "test":  DataLoader(image_datasets["test"],  batch_size=batch_size, shuffle=False, num_workers=0)
    }
    
    class_names = image_datasets["train"].classes
    return dataloaders, class_names


if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    DATA_PATH = PROJECT_ROOT / "data"
    
    loaders, classes = create_dataloaders(DATA_PATH)
    
    print("=" * 50)
    print(f"Detected Classes ({len(classes)}): {classes}")
    
    # Test unpacking a single batch
    images, labels = next(iter(loaders["train"]))
    
    print(f"Batch Images Tensor Shape: {images.shape}")
    print(f"Batch Labels Tensor Shape: {labels.shape}")
    print(f"First 5 Sample Labels:     {labels[:5].tolist()}")
    print("=" * 50)
    print("DataLoader pipeline initialized and verified successfully!")