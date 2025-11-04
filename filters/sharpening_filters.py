import numpy as np
from PIL import Image, ImageFilter 
import numpy as np
from scipy.ndimage import convolve

def highpass_filtering_with_laplacian_operator(image):
    kernel = np.array([[0, -1, 0],
                       [-1, 4, -1],
                       [0, -1, 0]])
    img_np = np.array(image, dtype=np.float32)
    if img_np.ndim == 2:
        filtered = convolve(img_np, kernel)
    else:
        filtered = np.zeros_like(img_np)
        for i in range(3):
            filtered[..., i] = convolve(img_np[..., i], kernel)
    filtered = np.clip(filtered, 0, 255)
    return Image.fromarray(filtered.astype(np.uint8))

def unsharp_masking(image):
    """Default kernel size 3, default strength"""
    blurred = image.filter(ImageFilter.GaussianBlur(radius=1))
    img_np = np.array(image, dtype=np.float32)
    blurred_np = np.array(blurred, dtype=np.float32)
    mask = img_np - blurred_np
    sharpened = img_np + mask
    sharpened = np.clip(sharpened, 0, 255)
    return Image.fromarray(sharpened.astype(np.uint8))

def highboost_filtering(image, boost_factor=2.0):
    blurred = image.filter(ImageFilter.GaussianBlur(radius=1))
    img_np = np.array(image, dtype=np.float32)
    blurred_np = np.array(blurred, dtype=np.float32)
    mask = img_np - blurred_np
    highboosted = img_np + boost_factor * mask
    highboosted = np.clip(highboosted, 0, 255)
    return Image.fromarray(highboosted.astype(np.uint8))
