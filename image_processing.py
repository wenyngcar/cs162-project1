from PIL import Image
import matplotlib.pyplot as plt
import io
from tkinter import simpledialog
import numpy as np

# Return three images showing R, G, and B channels separately.
def create_rgb_channel_images(img):
    r, g, b = img.split()
    r_img = Image.merge("RGB", (r, Image.new("L", r.size), Image.new("L", r.size)))
    g_img = Image.merge("RGB", (Image.new("L", g.size), g, Image.new("L", g.size)))
    b_img = Image.merge("RGB", (Image.new("L", b.size), Image.new("L", b.size), b))
    return r_img, g_img, b_img, (r, g, b)


# Generate histogram image from a single grayscale channel.
def create_histogram(channel_img, color):
    hist = channel_img.histogram()
    plt.figure(figsize=(3, 2))
    plt.bar(range(256), hist, color=color)
    plt.ylim(0, max(hist) * 1.1)
    plt.title(f"{color.capitalize()} Channel Histogram")
    plt.xlabel("Intensity")
    plt.ylabel("Frequency")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return Image.open(buf)

# Grayscale Transformation
def create_grayscale_image(img):
    r, g, b = img.split()
    gray_pixels = [
        int((r_val + g_val + b_val) / 3)
        for r_val, g_val, b_val in zip(r.getdata(), g.getdata(), b.getdata())
    ]
    gray_img = Image.new("L", img.size)
    gray_img.putdata(gray_pixels)
    return gray_img

# Negative Transformation (grayscale-based)
def create_negative_image(img):
    # Return the negative of the grayscale version of the image.
    # Convert to grayscale first
    gray_img = img.convert("L")
    
    # Invert pixel values
    inverted_img = Image.eval(gray_img, lambda px: 255 - px)
    
    return inverted_img

def create_threshold_image(img):
    # Convert image to black/white using a user-defined threshold (0-255).
    threshold = simpledialog.askinteger(
        "Threshold Input", "Enter threshold (0-255):", minvalue=0, maxvalue=255
    )
    if threshold is None:
        return None  # user canceled

    gray_img = img.convert("L")  # ensure grayscale
    bw_pixels = [255 if p >= threshold else 0 for p in gray_img.getdata()]
    bw_img = Image.new("L", gray_img.size)
    bw_img.putdata(bw_pixels)
    return bw_img

def create_gamma_image(img):
    """Apply gamma correction to the grayscale version of the image."""
    gamma = simpledialog.askfloat(
        "Gamma Input",
        "Enter gamma value (e.g., 0.5 for brighter, 2.0 for darker):",
        minvalue=0.1,
        maxvalue=10.0,
    )
    if gamma is None:
        return None  # user canceled

    gray_img = img.convert("L")
    img_np = np.array(gray_img).astype(np.float32) / 255.0
    gamma_corrected = np.power(img_np, gamma)
    gamma_img = Image.fromarray(np.uint8(np.clip(gamma_corrected * 255, 0, 255)))
    return gamma_img
