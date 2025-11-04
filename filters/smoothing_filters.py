from PIL import Image, ImageFilter
import numpy as np
from scipy.ndimage import uniform_filter

def apply_average_filter(image):
    """Simple averaging filter (3x3)"""
    img_np = np.array(image, dtype=np.uint8)
    if img_np.ndim == 2:  # grayscale
        img_filtered = uniform_filter(img_np, size=3)
    else:  # color
        img_filtered = np.zeros_like(img_np)
        for i in range(3):  # RGB channels
            img_filtered[..., i] = uniform_filter(img_np[..., i], size=3)
    return Image.fromarray(img_filtered.astype(np.uint8))

def apply_median_filter(image):
    """Median filter (3x3)"""
    img_np = np.array(image, dtype=np.uint8)
    from scipy.ndimage import median_filter
    if img_np.ndim == 2:
        img_filtered = median_filter(img_np, size=3)
    else:
        img_filtered = np.zeros_like(img_np)
        for i in range(3):
            img_filtered[..., i] = median_filter(img_np[..., i], size=3)
    return Image.fromarray(img_filtered.astype(np.uint8))
