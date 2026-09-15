"""
scripts/setup_dataset.py
Verifies image integrity and performs a stratified 70/15/15 train/val/test split.
"""

import shutil
import random
from pathlib import Path
from PIL import Image

def is_valid_image(file_path: Path) -> bool:
    """Check if file can be opened and verified by PIL."""
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def split_dataset(
    raw_dir: str = "data/raw",
    output_dir: str = "data/processed",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    seed: int = 42
):
    random.seed(seed)
    raw_path = Path(raw_dir)
    out_path = Path(output_dir)

    if not raw_path.exists():
        print(f"Error: Raw directory '{raw_path}' does not exist.")
        print("Please place species subfolders inside 'data/raw/'.")
        return

    # Discover species subdirectories
    classes = [d for d in raw_path.iterdir() if d.is_dir()]
    if not classes:
        print(f"No species folders found in '{raw_path}'.")
        return

    print(f"Found {len(classes)} classes: {[c.name for c in classes]}")

    for split in ["train", "val", "test"]:
        for cls_dir in classes:
            (out_path / split / cls_dir.name).mkdir(parents=True, exist_ok=True)

    summary = {c.name: {"train": 0, "val": 0, "test": 0, "corrupted": 0} for c in classes}

    for cls_dir in classes:
        images = [f for f in cls_dir.iterdir() if f.is_file()]
        random.shuffle(images)

        valid_images = []
        for img in images:
            if is_valid_image(img):
                valid_images.append(img)
            else:
                summary[cls_dir.name]["corrupted"] += 1

        n_total = len(valid_images)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)

        splits = {
            "train": valid_images[:n_train],
            "val": valid_images[n_train:n_train + n_val],
            "test": valid_images[n_train + n_val:]
        }

        for split_name, split_files in splits.items():
            for src_file in split_files:
                dst_file = out_path / split_name / cls_dir.name / src_file.name
                shutil.copy2(src_file, dst_file)
                summary[cls_dir.name][split_name] += 1

    print("\nDataset Split Summary:")
    print("-" * 60)
    for cls_name, stats in summary.items():
        print(f"{cls_name:<20} Train: {stats['train']:<5} Val: {stats['val']:<5} Test: {stats['test']:<5} Corrupt: {stats['corrupted']}")
    print("-" * 60)
    print(f"Processed dataset saved to: {out_path.resolve()}")

if __name__ == "__main__":
    split_dataset()