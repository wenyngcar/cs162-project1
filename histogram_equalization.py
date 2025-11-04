import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io

def histogram_equalization(gray_img: Image.Image) -> tuple[Image.Image, Image.Image]:
    """
    Apply histogram equalization to a grayscale image.
    Returns: (equalized_image, histogram_comparison_image)
    """
    img_array = np.array(gray_img)
    
    # Compute histogram
    hist = np.bincount(img_array.ravel(), minlength=256)
    
    # Calculate CDF
    cdf = hist.cumsum()
    cdf_normalized = (cdf - cdf.min()) * 255 / (cdf.max() - cdf.min())
    cdf_normalized = cdf_normalized.astype(np.uint8)
    
    # Create equalized image
    equalized_array = cdf_normalized[img_array]
    equalized_img = Image.fromarray(equalized_array, mode='L')
    
    # Calculate equalized histogram
    hist_eq = np.bincount(equalized_array.ravel(), minlength=256)
    
    # Create histogram comparison image
    plt.figure(figsize=(8, 4))
    
    plt.subplot(1, 2, 1)
    plt.bar(range(256), hist, color='gray', width=1.0)
    plt.title('Original Histogram')
    plt.xlabel('Intensity')
    plt.ylabel('Frequency')
    
    plt.subplot(1, 2, 2)
    plt.bar(range(256), hist_eq, color='green', width=1.0)
    plt.title('Equalized Histogram')
    plt.xlabel('Intensity')
    plt.ylabel('Frequency')
    
    plt.tight_layout()
    
    # Convert plot to PIL Image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    hist_img = Image.open(buf)
    
    return equalized_img, hist_img