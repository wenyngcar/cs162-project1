import numpy as np
from PIL import Image


def _ensure_grayscale(image: Image.Image) -> Image.Image:
    if image.mode != "L":
        return image.convert("L")
    return image


def apply_average_filter(image: Image.Image, kernel_size: int = 3) -> Image.Image:
    """Apply an averaging (mean) filter to a grayscale image."""
    if kernel_size % 2 == 0 or kernel_size < 3:
        raise ValueError("kernel_size must be an odd integer >= 3")

    gray = _ensure_grayscale(image)
    img_np = np.array(gray, dtype=np.float32)

    k = kernel_size
    pad = k // 2
    padded = np.pad(img_np, pad_width=pad, mode="reflect")

    height, width = img_np.shape
    result = np.empty_like(img_np)

    for y in range(height):
        for x in range(width):
            window = padded[y:y+k, x:x+k]
            result[y, x] = window.mean()

    result = np.clip(result, 0, 255).astype(np.uint8)
    return Image.fromarray(result, mode="L")


def apply_median_filter(image: Image.Image, kernel_size: int = 3) -> Image.Image:
    """Apply a median filter to a grayscale image."""
    if kernel_size % 2 == 0 or kernel_size < 3:
        raise ValueError("kernel_size must be an odd integer >= 3")

    gray = _ensure_grayscale(image)
    img_np = np.array(gray, dtype=np.uint8)

    pad = kernel_size // 2
    padded = np.pad(img_np, pad_width=pad, mode="reflect")

    height, width = img_np.shape
    result = np.empty_like(img_np)

    for y in range(height):
        y0 = y
        y1 = y + kernel_size
        for x in range(width):
            x0 = x
            x1 = x + kernel_size
            window = padded[y0:y1, x0:x1]
            result[y, x] = np.median(window)

    return Image.fromarray(result, mode="L")


