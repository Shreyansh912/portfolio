"""
download_data.py
Downloads images for 5 bird species and partitions them into
train (70%), val (15%), and test (15%) splits.
"""

import os
import shutil
import time
from pathlib import Path
import requests
from PIL import Image
from duckduckgo_search import DDGS

# Project directory paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Target classes and targeted search terms to fetch clean photos
SPECIES_QUERIES = {
    "american_robin": "american robin bird photo",
    "bald_eagle": "bald eagle bird photo",
    "blue_jay": "blue jay bird photo",
    "house_sparrow": "house sparrow bird photo",
    "mallard": "mallard duck bird photo"
}

TOTAL_PER_CLASS = 100
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
# Remainder goes to test (0.15)


def is_valid_image(file_path: Path) -> bool:
    """Verifies that the downloaded file is a readable RGB image."""
    try:
        with Image.open(file_path) as img:
            img.verify()
        # Re-open to verify conversion to RGB
        with Image.open(file_path) as img:
            img.convert("RGB")
        return True
    except Exception:
        return False


def download_species_images():
    ddgs = DDGS()

    for label, query in SPECIES_QUERIES.items():
        print(f"\nSearching images for: {label}...")
        raw_folder = DATA_DIR / "raw" / label
        raw_folder.mkdir(parents=True, exist_ok=True)

        results = ddgs.images(
            query,
            region="wt-wt",
            safesearch="off",
            max_results=TOTAL_PER_CLASS + 30  # Fetch extra buffer for corrupted links
        )

        valid_count = 0
        for i, item in enumerate(results):
            if valid_count >= TOTAL_PER_CLASS:
                break

            img_url = item.get("image")
            if not img_url:
                continue

            target_file = raw_folder / f"{label}_{valid_count:03d}.jpg"
            try:
                response = requests.get(img_url, timeout=5)
                if response.status_code == 200:
                    with open(target_file, "wb") as f:
                        f.write(response.content)

                    # Validate the image
                    if is_valid_image(target_file):
                        valid_count += 1
                    else:
                        target_file.unlink(missing_ok=True)
            except Exception:
                target_file.unlink(missing_ok=True)

        print(f"Downloaded {valid_count} verified images for {label}.")


def split_dataset():
    """Distributes raw images into train, val, and test partitions."""
    print("\nSplitting images into train, val, and test folders...")

    for label in SPECIES_QUERIES.keys():
        raw_folder = DATA_DIR / "raw" / label
        images = sorted(list(raw_folder.glob("*.jpg")))

        total = len(images)
        train_end = int(total * TRAIN_RATIO)
        val_end = train_end + int(total * VAL_RATIO)

        train_imgs = images[:train_end]
        val_imgs = images[train_end:val_end]
        test_imgs = images[val_end:]

        splits = {
            "train": train_imgs,
            "val": val_imgs,
            "test": test_imgs
        }

        for split_name, img_list in splits.items():
            dest_dir = DATA_DIR / split_name / label
            dest_dir.mkdir(parents=True, exist_ok=True)
            for img_path in img_list:
                shutil.copy(img_path, dest_dir / img_path.name)

        print(f"[{label}] Train: {len(train_imgs)} | Val: {len(val_imgs)} | Test: {len(test_imgs)}")

    print("\nDataset generation and partitioning complete!")


if __name__ == "__main__":
    download_species_images()
    split_dataset()