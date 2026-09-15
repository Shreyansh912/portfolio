"""
setup_structure.py
Automates the creation of the project folder layout and data directories.
"""

from pathlib import Path

# Define root and subdirectories
PROJECT_ROOT = Path(__file__).resolve().parent

DIRS_TO_CREATE = [
    # Data partitions
    PROJECT_ROOT / "data" / "raw",
    PROJECT_ROOT / "data" / "train",
    PROJECT_ROOT / "data" / "val",
    PROJECT_ROOT / "data" / "test",
    # Source code
    PROJECT_ROOT / "src",
    # Saved model weights
    PROJECT_ROOT / "models",
    # Results & figures
    PROJECT_ROOT / "results" / "plots",
    PROJECT_ROOT / "results" / "confusion_matrix",
    # Web application
    PROJECT_ROOT / "app",
]

# The 5 species classes
CLASSES = [
    "american_robin",
    "bald_eagle",
    "blue_jay",
    "house_sparrow",
    "mallard",
]

def build_scaffolding():
    # 1. Create base folders
    for directory in DIRS_TO_CREATE:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created: {directory.relative_to(PROJECT_ROOT)}")

    # 2. Create class subfolders inside train, val, and test
    for split in ["train", "val", "test"]:
        for bird_class in CLASSES:
            class_folder = PROJECT_ROOT / "data" / split / bird_class
            class_folder.mkdir(parents=True, exist_ok=True)

    print("\nProject directories and 5 species folders initialized successfully.")

if __name__ == "__main__":
    build_scaffolding()