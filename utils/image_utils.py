from PIL import Image, ImageDraw, ImageTk
import matplotlib.pyplot as plt
import io

def thumbnail_photo(image, max_size):
    """Return a PhotoImage resized to fit within max_size (w, h)."""
    copy = image.copy()
    copy.thumbnail(max_size)
    return ImageTk.PhotoImage(copy)

def set_widget_image(widgets, key, photo):
    """Assign a Tk PhotoImage to a widget and keep a reference."""
    widgets[key].config(image=photo)
    widgets[key].image = photo

def render_palette_preview(palette, cols=16, swatch=20):
    """Build a palette preview image from an RGB palette list."""
    width = cols * swatch
    rows = max(1, (len(palette) + cols - 1) // cols)
    height = rows * swatch
    pal_img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(pal_img)
    for i, color in enumerate(palette):
        x, y = (i % cols) * swatch, (i // cols) * swatch
        draw.rectangle([x, y, x + swatch - 1, y + swatch - 1], fill=color, outline="gray")
    return pal_img

def render_grayscale_histogram(gray_img):
    """Create a PIL image of the grayscale histogram."""
    gray_hist = gray_img.histogram()
    plt.figure(figsize=(4, 3))
    plt.bar(range(256), gray_hist, color="gray")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return Image.open(buf)
