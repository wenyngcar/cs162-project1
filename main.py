from tkinter import Tk, filedialog, Label, simpledialog
from PIL import Image, ImageDraw, ImageTk
import os, io, matplotlib.pyplot as plt
from pcx_reader import read_pcx_header, read_pcx_palette, decompress_rle
from image_processing import (
    create_grayscale_image,
    create_negative_image,
    create_gamma_image,
    create_rgb_channel_images,
    create_histogram,
    create_threshold_image,
)
from ui_components import create_main_ui
from histogram_equalization import histogram_equalization
from filters.smoothing_filters import apply_average_filter, apply_median_filter

# Registry of available filters and their parameter prompts
FILTERS = {
    "Averaging": {
        "fn": apply_average_filter,
        "params": [("kernel_size", "int", 3, {"min": 3, "odd": True})],
    },
    "Median": {
        "fn": apply_median_filter,
        "params": [("kernel_size", "int", 3, {"min": 3, "odd": True})],
    },
}

def _thumbnail_photo(image, max_size):
    """Return a PhotoImage from a PIL image resized to fit within max_size (w, h)."""
    copy = image.copy()
    copy.thumbnail(max_size)
    return ImageTk.PhotoImage(copy)


def _set_widget_image(widgets, key, photo):
    """Assign a Tk PhotoImage to the widget referenced by key and keep a ref."""
    widgets[key].config(image=photo)
    widgets[key].image = photo


def _render_palette_preview(palette, cols=16, swatch=20):
    """Build a small palette preview image from an RGB palette list."""
    width = cols * swatch
    rows = max(1, (len(palette) + cols - 1) // cols)
    height = rows * swatch
    pal_img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(pal_img)
    for i, color in enumerate(palette):
        x, y = (i % cols) * swatch, (i // cols) * swatch
        draw.rectangle([x, y, x + swatch - 1, y + swatch - 1], fill=color, outline='gray')
    return pal_img


def _render_grayscale_histogram(gray_img):
    """Create a PIL image of the grayscale histogram for display."""
    gray_hist = gray_img.histogram()
    plt.figure(figsize=(4, 3))
    plt.bar(range(256), gray_hist, color='gray')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return Image.open(buf)

def open_pcx(widgets):
    filepath = filedialog.askopenfilename(filetypes=[("PCX files", "*.pcx")])
    if not filepath:
        return
    try:
        header = read_pcx_header(filepath)
        if header['BitsPerPixel'] != 8 or header['NPlanes'] != 1:
            raise ValueError("Only 8-bit single-plane PCX files supported.")
        palette = read_pcx_palette(filepath)
        pixels = decompress_rle(filepath)

        width, height = header['Width'], header['Height']
        img = Image.new('RGB', (width, height))
        img.putdata([palette[p] for p in pixels[:width * height]])

        # Header text
        info = [f"{k}: {v}" for k, v in header.items()]
        widgets["header"].delete(1.0, "end")
        widgets["header"].insert(1.0, '\n'.join(info))
        
        # Original Image (clickable for RGB values)
        original_img = img.copy()
        original_photo = _thumbnail_photo(original_img, (400, 400))
        _set_widget_image(widgets, "original_img", original_photo)

        scale_x = original_img.width / original_photo.width()
        scale_y = original_img.height / original_photo.height()

        def show_rgb_values(event):
            x = int(event.x * scale_x)
            y = int(event.y * scale_y)
            if 0 <= x < original_img.width and 0 <= y < original_img.height:
                r, g, b = original_img.getpixel((x, y))
                widgets["rgb_info"].config(
                    text=f"Position: ({x}, {y}) | RGB: ({r}, {g}, {b}) | R={r}, G={g}, B={b}"
                )
            else:
                widgets["rgb_info"].config(text="Click inside the image to see RGB values")

        widgets["original_img"].bind("<Button-1>", show_rgb_values)

        # Palette preview
        pal_img = _render_palette_preview(palette)
        _set_widget_image(widgets, "palette", _thumbnail_photo(pal_img, (400, 400)))

        # Main decompressed image
        _set_widget_image(widgets, "img", _thumbnail_photo(img, (400, 400)))

        # RGB channels and their histograms
        r_img, g_img, b_img, (r_channel, g_channel, b_channel) = create_rgb_channel_images(img)
        _set_widget_image(widgets, "red", _thumbnail_photo(r_img, (250, 250)))
        _set_widget_image(widgets, "green", _thumbnail_photo(g_img, (250, 250)))
        _set_widget_image(widgets, "blue", _thumbnail_photo(b_img, (250, 250)))

        _set_widget_image(widgets, "red_hist", _thumbnail_photo(create_histogram(r_channel, 'red'), (250, 180)))
        _set_widget_image(widgets, "green_hist", _thumbnail_photo(create_histogram(g_channel, 'green'), (250, 180)))
        _set_widget_image(widgets, "blue_hist", _thumbnail_photo(create_histogram(b_channel, 'blue'), (250, 180)))

        # Grayscale view and histogram
        gray_img = create_grayscale_image(img)
        _set_widget_image(widgets, "gray", _thumbnail_photo(gray_img, (400, 400)))
        gray_hist_img = _render_grayscale_histogram(gray_img)
        _set_widget_image(widgets, "gray_hist", _thumbnail_photo(gray_hist_img, (400, 400)))
        # Store grayscale image for later operations
        widgets["gray_image_obj"] = gray_img

        # Negative Image
        neg_img = create_negative_image(gray_img)
        if "negative" not in widgets:
            neg_label_title = Label(widgets["gray"].master.master, text="Negative Image:", font=("Arial", 11, "bold"))
            neg_label_title.pack(anchor="w")
            neg_label = Label(widgets["gray"].master.master, bg="white", relief="sunken")
            neg_label.pack(pady=10)
            widgets["negative"] = neg_label
        _set_widget_image(widgets, "negative", _thumbnail_photo(neg_img, (400, 400)))

        # --- Black/White via Manual Thresholding ---
        bw_img = create_threshold_image(gray_img)
        if bw_img:
            if "bw" not in widgets:
                bw_label_title = Label(widgets["gray"].master.master, text="Black/White (Manual Thresholding):", font=("Arial", 11, "bold"))
                bw_label_title.pack(anchor="w")
                bw_label = Label(widgets["gray"].master.master, bg="white", relief="sunken")
                bw_label.pack(pady=10)
                widgets["bw"] = bw_label
            _set_widget_image(widgets, "bw", _thumbnail_photo(bw_img, (400, 400)))



# --- Power-Law (Gamma) Transformation ---
        gamma_img = create_gamma_image(gray_img)
        if gamma_img:
            if "gamma" not in widgets:
                gamma_label_title = Label(widgets["gray"].master.master, text="Power-Law (Gamma) Transformation:", font=("Arial", 11, "bold"))
                gamma_label_title.pack(anchor="w")
                gamma_label = Label(widgets["gray"].master.master, bg="white", relief="sunken")
                gamma_label.pack(pady=10)
                widgets["gamma"] = gamma_label
            _set_widget_image(widgets, "gamma", _thumbnail_photo(gamma_img, (400, 400)))

        widgets["status"].config(text=f"Loaded: {os.path.basename(filepath)}", fg="green")

    except Exception as e:
        widgets["status"].config(text=f"Error: {e}", fg="red")
        import traceback
        traceback.print_exc()
# --- Histogram Equalization ---
    histogram_equalization(filepath)
    

def main():
    root = Tk()
    root.title("PCX File Reader with RGB Histograms")
    root.geometry("1000x800")

    widgets = create_main_ui(root, lambda: open_pcx(widgets=None))
    # Late binding fix:
    widgets["status"].after(100, lambda: widgets.update({"open": lambda: open_pcx(widgets)}))
    widgets["status"].after(100, lambda: root.bind("<Control-o>", lambda e: open_pcx(widgets)))

    # Rewire the open button to pass widgets
    for w in root.winfo_children():
        if isinstance(w, Label) or w.cget("text") == "Open PCX File":
            w.configure(command=lambda: open_pcx(widgets))
            break

    # Populate filter dropdown and wire generic handler
    def _populate_filter_menu():
        select_widget = widgets.get("filter_select")
        var = widgets.get("filter_select_var")
        if not select_widget or not var:
            return
        menu = select_widget["menu"]
        menu.delete(0, "end")
        names = list(FILTERS.keys())
        default = names[0] if names else ""
        var.set(default)
        for name in names:
            menu.add_command(label=name, command=lambda n=name: var.set(n))

    def _prompt_params(params_spec):
        values = {}
        for name, kind, default, rules in params_spec:
            if kind == "int":
                minvalue = rules.get("min") if rules else None
                maxvalue = rules.get("max") if rules else None
                val = simpledialog.askinteger(
                    "Parameter",
                    f"Enter {name}:",
                    initialvalue=default,
                    minvalue=minvalue,
                    maxvalue=maxvalue,
                )
                if val is None:
                    return None
                if rules and rules.get("odd") and val % 2 == 0:
                    widgets["status"].config(text=f"{name} must be odd.", fg="red")
                    return None
            elif kind == "float":
                minvalue = rules.get("min") if rules else None
                maxvalue = rules.get("max") if rules else None
                val = simpledialog.askfloat(
                    "Parameter",
                    f"Enter {name}:",
                    initialvalue=default,
                    minvalue=minvalue,
                    maxvalue=maxvalue,
                )
                if val is None:
                    return None
            else:
                val = default
            values[name] = val
        return values

    def _apply_selected_filter():
        src = widgets.get("gray_image_obj")
        if src is None:
            widgets["status"].config(text="Load an image first.", fg="red")
            return
        var = widgets.get("filter_select_var")
        choice = var.get() if var else None
        spec = FILTERS.get(choice)
        if not spec:
            widgets["status"].config(text="Select a filter.", fg="red")
            return
        params = _prompt_params(spec.get("params", []))
        if params is None:
            return
        try:
            out = spec["fn"](src, **params)
            _set_widget_image(widgets, "filter_result_img", _thumbnail_photo(out, (400, 400)))
            widgets["status"].config(text=f"Applied {choice}", fg="green")
        except Exception as ex:
            widgets["status"].config(text=f"Error: {ex}", fg="red")

    _populate_filter_menu()
    if "apply_filter_btn" in widgets:
        widgets["apply_filter_btn"].configure(command=_apply_selected_filter)

    root.mainloop()

if __name__ == "__main__":
    main()
