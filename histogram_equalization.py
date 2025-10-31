import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from pcx_reader import read_pcx_header, read_pcx_palette, decompress_rle

def histogram_equalization(image_path):
    header = read_pcx_header(image_path)
    palette = read_pcx_palette(image_path)
    pixels = decompress_rle(image_path)
    
    width, height = header['Width'], header['Height']
    
    # Create grayscale image
    img = Image.new('RGB', (width, height))
    img.putdata([palette[p] for p in pixels[:width * height]])
    gray_img = img.convert('L')
    img_array = np.array(gray_img)
    
    # Compute histogram
    hist = np.bincount(img_array.ravel(), minlength=256)
    
    # Calculate CDF
    cdf = hist.cumsum()
    cdf_normalized = (cdf - cdf.min()) * 255 / (cdf.max() - cdf.min())
    cdf_normalized = cdf_normalized.astype(np.uint8)
    
    # Create equalized image
    equalized_array = cdf_normalized[img_array]
    
    # Calculate equalized histogram
    hist_eq = np.bincount(equalized_array.ravel(), minlength=256)
    
    # Display results
    plt.figure(figsize=(12, 8))
    
    # Original image and histogram
    plt.subplot(2, 2, 1)
    plt.imshow(img_array, cmap='gray')
    plt.title('Original Image')
    plt.axis('off')
    
    plt.subplot(2, 2, 2)
    plt.bar(range(256), hist, color='gray', width=1.0)
    plt.title('Original Histogram')
    plt.xlabel('Intensity')
    plt.ylabel('Frequency')
    
    # Equalized image and histogram
    plt.subplot(2, 2, 3)
    plt.imshow(equalized_array, cmap='gray')
    plt.title('Equalized Image')
    plt.axis('off')
    
    plt.subplot(2, 2, 4)
    plt.bar(range(256), hist_eq, color='green', width=1.0)
    plt.title('Equalized Histogram')
    plt.xlabel('Intensity')
    plt.ylabel('Frequency')
    
    plt.tight_layout()
    plt.show()