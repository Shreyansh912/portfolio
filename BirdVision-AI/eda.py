"""
eda.py
Exploratory Data Analysis: inspects splits, checks image dimensions,
and visualizes sample images per species.
"""

from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results" / "plots"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SPLITS = ["train", "val", "test"]

def analyze_counts():
    print("=" * 55)
    print("         DATASET DISTRIBUTION SUMMARY")
    print("=" * 55)
    
    # Track counts per class across splits
    species_list = sorted([d.name for d in (DATA_DIR / "train").iterdir() if d.is_dir()])
    
    header = f"{'Species':<20} | {'Train':<7} | {'Val':<7} | {'Test':<7} | {'Total':<7}"
    print(header)
    print("-" * len(header))
    
    totals = {"train": 0, "val": 0, "test": 0}
    
    for species in species_list:
        counts = {}
        for split in SPLITS:
            folder = DATA_DIR / split / species
            n_files = len(list(folder.glob("*.jpg")))
            counts[split] = n_files
            totals[split] += n_files
        
        species_total = sum(counts.values())
        print(f"{species:<20} | {counts['train']:<7} | {counts['val']:<7} | {counts['test']:<7} | {species_total:<7}")
    
    print("-" * len(header))
    overall = sum(totals.values())
    print(f"{'TOTAL':<20} | {totals['train']:<7} | {totals['val']:<7} | {totals['test']:<7} | {overall:<7}\n")

def check_image_dimensions():
    print("--- Image Resolution Inspection (Train Split) ---")
    train_dir = DATA_DIR / "train"
    sample_images = list(train_dir.glob("*/*.jpg"))[:50]
    
    widths = []
    heights = []
    
    for img_path in sample_images:
        with Image.open(img_path) as img:
            w, h = img.size
            widths.append(w)
            heights.append(h)
            
    print(f"Sampled: {len(sample_images)} images")
    print(f"Min dimensions: {min(widths)}x{min(heights)}")
    print(f"Max dimensions: {max(widths)}x{max(heights)}")
    print(f"Average size:   {int(sum(widths)/len(widths))}x{int(sum(heights)/len(heights))}")
    print("Takeaway: Images have varying sizes. Resizing is strictly required before batching!\n")

def visualize_samples():
    print("Generating sample visualization...")
    train_dir = DATA_DIR / "train"
    classes = sorted([d.name for d in train_dir.iterdir() if d.is_dir()])
    
    fig, axes = plt.subplots(1, len(classes), figsize=(15, 3.5))
    
    for idx, class_name in enumerate(classes):
        images = list((train_dir / class_name).glob("*.jpg"))
        if not images:
            continue
        sample_path = images[0]
        with Image.open(sample_path) as img:
            axes[idx].imshow(img)
            axes[idx].set_title(class_name.replace("_", " ").title(), fontsize=10)
            axes[idx].axis("off")
            
    plt.tight_layout()
    plot_path = RESULTS_DIR / "dataset_samples.png"
    plt.savefig(plot_path, dpi=200)
    print(f"Saved visual sample grid to: {plot_path.relative_to(BASE_DIR)}")
    #plt.show()

if __name__ == "__main__":
    analyze_counts()
    check_image_dimensions()
    visualize_samples()