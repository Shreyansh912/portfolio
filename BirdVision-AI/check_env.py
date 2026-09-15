import torch
import torchvision
import numpy as np

print("=" * 45)
print("       ENVIRONMENT DIAGNOSTICS")
print("=" * 45)
print(f"PyTorch Version: {torch.__version__}")
print(f"CUDA Available:  {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU Model:       {torch.cuda.get_device_name(0)}")
    
    # Test tensor allocation in GPU memory
    test_tensor = torch.ones((3, 3), device="cuda")
    print("GPU VRAM Test:   Passed successfully!")
else:
    print("Device:          CPU mode")

print("\n--- Shape Verification ---")
raw_img = np.zeros((224, 224, 3), dtype=np.uint8)
print(f"NumPy Raw Shape (H, W, C):   {raw_img.shape}")

tensor_img = torch.from_numpy(raw_img).permute(2, 0, 1)
print(f"PyTorch Tensor (C, H, W):    {tensor_img.shape}")
print("=" * 45)