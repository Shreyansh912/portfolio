"""
download_birds.py
Downloads the birds-species-9dp5b dataset in YOLOv8 format.
"""

from roboflow import Roboflow

# Initialize Roboflow with your API key
rf = Roboflow(api_key="7uHT42WowxXfy0DEfpWT")

# Connect to the workspace and project
project = rf.workspace("farhan-ad6lk").project("birds-species-9dp5b")
version = project.version(1)

# Download in YOLOv8 format directly to a local directory
dataset = version.download("yolov8")

print("=" * 50)
print(f"Dataset successfully downloaded to: {dataset.location}")
print("=" * 50)