# Gradient: Sobel magnitude operator
from PIL import Image
import numpy as np


def gradient_sobel(image: Image.Image) -> Image.Image:
    """
    Apply Sobel gradient magnitude operator for edge detection.
    Computes the gradient magnitude using Sobel operators in x and y directions.
    Magnitude = sqrt(Gx² + Gy²)
    """
    img_np = np.array(image.convert("L"), dtype=np.float32)
    
    # Sobel kernels for horizontal (Gx) and vertical (Gy) gradients
    sobel_x = np.array([
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ])
    
    sobel_y = np.array([
        [-1, -2, -1],
        [0, 0, 0],
        [1, 2, 1]
    ])
    
    # Apply convolution
    k_h, k_w = sobel_x.shape
    pad_h, pad_w = k_h // 2, k_w // 2
    padded = np.pad(img_np, pad_width=((pad_h, pad_h), (pad_w, pad_w)), mode="reflect")
    
    height, width = img_np.shape
    gx = np.zeros_like(img_np, dtype=np.float32)
    gy = np.zeros_like(img_np, dtype=np.float32)
    
    # Compute gradients in x and y directions
    for y in range(height):
        for x in range(width):
            window = padded[y:y+k_h, x:x+k_w]
            gx[y, x] = np.sum(window * sobel_x)
            gy[y, x] = np.sum(window * sobel_y)
    
    # Compute gradient magnitude: sqrt(Gx² + Gy²)
    magnitude = np.sqrt(gx**2 + gy**2)
    
    # Normalize to 0-255 range
    magnitude = np.clip(magnitude, 0, 255).astype(np.uint8)
    
    return Image.fromarray(magnitude, mode="L")
