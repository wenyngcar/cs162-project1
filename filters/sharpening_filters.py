import numpy as np
from PIL import Image


def highpass_filtering_with_laplacian_operator(image: Image.Image) -> Image.Image:
    """
    Apply Laplacian highpass filter for sharpening.
    Filter used: 4-neighbor Laplacian kernel
    """
    img_np = np.array(image, dtype=np.float32)
    
    # Laplacian kernel (4-neighbor version)
    kernel = np.array([
        [0, -1, 0],
        [-1, 4, -1],
        [0, -1, 0]
    ])
    
    # Apply kernel using convolution
    k_h, k_w = kernel.shape
    pad_h, pad_w = k_h // 2, k_w // 2
    padded = np.pad(img_np, pad_width=((pad_h, pad_h), (pad_w, pad_w)), mode="reflect")
    
    height, width = img_np.shape
    filtered = np.zeros_like(img_np, dtype=np.float32)
    
    for y in range(height):
        for x in range(width):
            window = padded[y:y+k_h, x:x+k_w]
            filtered[y, x] = np.sum(window * kernel)
    
    # Add to original for sharpening: g(x,y) = f(x,y) + c * ∇²f
    result = img_np + filtered
    
    result = np.clip(result, 0, 255).astype(np.uint8)
    return Image.fromarray(result, mode="L")


def unsharp_masking(image: Image.Image, kernel_size: int = 3) -> Image.Image:
    """
    Apply unsharp masking for sharpening.
    Amplification parameter k = 1.0
    """
    img_np = np.array(image, dtype=np.float32)
    
    # Create blurred version (simple averaging)
    k = kernel_size
    pad = k // 2
    padded = np.pad(img_np, pad_width=pad, mode="reflect")
    blurred = np.zeros_like(img_np)
    
    for y in range(img_np.shape[0]):
        for x in range(img_np.shape[1]):
            window = padded[y:y+k, x:x+k]
            blurred[y, x] = window.mean()
    
    # Unsharp masking: g(x,y) = f(x,y) + k * (f(x,y) - f_blur(x,y))
    # where k is the amplification parameter (set to 1.0 here)
    mask = img_np - blurred
    result = img_np + mask
    
    result = np.clip(result, 0, 255).astype(np.uint8)
    return Image.fromarray(result, mode="L")


def highboost_filtering(image: Image.Image, boost_factor: float = 2.0, kernel_size: int = 3) -> Image.Image:
    """Apply highboost filtering for enhanced sharpening."""
    img_np = np.array(image, dtype=np.float32)
    
    # Create blurred version
    k = kernel_size
    pad = k // 2
    padded = np.pad(img_np, pad_width=pad, mode="reflect")
    blurred = np.zeros_like(img_np)
    
    for y in range(img_np.shape[0]):
        for x in range(img_np.shape[1]):
            window = padded[y:y+k, x:x+k]
            blurred[y, x] = window.mean()
    
    # Highboost: g(x,y) = A * f(x,y) - (A-1) * f_blur(x,y)
    result = boost_factor * img_np - (boost_factor - 1.0) * blurred
    
    result = np.clip(result, 0, 255).astype(np.uint8)
    return Image.fromarray(result, mode="L")