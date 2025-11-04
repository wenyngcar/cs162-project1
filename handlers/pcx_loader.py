import os
from tkinter import filedialog, Label, Button, Toplevel
from PIL import Image, ImageTk
from pcx_reader import read_pcx_header, read_pcx_palette, decompress_rle
from image_processing import create_grayscale_image, create_rgb_channel_images, create_histogram
from utils.image_utils import (
    thumbnail_photo,
    set_widget_image,
    render_palette_preview,
)
from handlers.popup_windows import (
    show_threshold_window,
    show_gamma_window,
    show_negative_window,
    show_hist_eq_window,
)

def open_pcx(widgets):
    """Open and display a PCX file along with its RGB, grayscale, and histogram data."""
    filepath = filedialog.askopenfilename(filetypes=[("PCX files", "*.pcx")])
    if not filepath:
        return

    try:
        # ========== READ PCX HEADER AND DATA ==========
        header = read_pcx_header(filepath)
        if header["BitsPerPixel"] != 8 or header["NPlanes"] != 1:
            raise ValueError("Only 8-bit single-plane PCX files are supported.")

        palette = read_pcx_palette(filepath)
        pixels = decompress_rle(filepath)
        width, height = header["Width"], header["Height"]

        # ========== BUILD IMAGE FROM RAW DATA ==========
        img = Image.new("RGB", (width, height))
        img.putdata([palette[p] for p in pixels[:width * height]])

        widgets["current_image"] = img

        # ? Create and store grayscale image immediately
        gray_img = create_grayscale_image(img)
        widgets["gray_image"] = gray_img

        # ========== DISPLAY HEADER INFORMATION ==========
        widgets["header"].delete(1.0, "end")
        widgets["header"].insert(1.0, "\n".join([f"{k}: {v}" for k, v in header.items()]))

        # ========== DISPLAY ORIGINAL IMAGE ==========
        original_img = img.copy()
        original_photo = thumbnail_photo(original_img, (400, 400))
        set_widget_image(widgets, "original_img", original_photo)

        # Set up RGB value on click
        scale_x = original_img.width / original_photo.width()
        scale_y = original_img.height / original_photo.height()

        def show_rgb_values(event):
            x = int(event.x * scale_x)
            y = int(event.y * scale_y)
            if 0 <= x < original_img.width and 0 <= y < original_img.height:
                r, g, b = original_img.getpixel((x, y))
                widgets["rgb_info"].config(
                    text=f"Position: ({x}, {y}) | RGB: ({r}, {g}, {b})"
                )

        widgets["original_img"].bind("<Button-1>", show_rgb_values)

        # ========== DISPLAY PALETTE AND IMAGE ==========
        pal_img = render_palette_preview(palette)
        set_widget_image(widgets, "palette", thumbnail_photo(pal_img, (400, 400)))
        set_widget_image(widgets, "img", thumbnail_photo(img, (400, 400)))
        widgets["current_image"] = img

        # ========== RGB CHANNELS & HISTOGRAMS ==========
        r_img, g_img, b_img, (r_channel, g_channel, b_channel) = create_rgb_channel_images(img)
        r_hist = create_histogram(r_channel, "red")
        g_hist = create_histogram(g_channel, "green")
        b_hist = create_histogram(b_channel, "blue")

        def show_channel_window(channel_name, channel_img, hist_img):
            win = Toplevel()
            win.title(f"{channel_name} Channel and Histogram")

            Label(win, text=f"{channel_name} Channel Image").pack()
            channel_photo = ImageTk.PhotoImage(channel_img.resize((300, 300)))
            lbl1 = Label(win, image=channel_photo)
            lbl1.image = channel_photo
            lbl1.pack(pady=5)

            hist_photo = ImageTk.PhotoImage(hist_img.resize((300, 200)))
            lbl2 = Label(win, image=hist_photo)
            lbl2.image = hist_photo
            lbl2.pack(pady=5)

        widgets["red_btn"].configure(command=lambda: show_channel_window("Red", r_img, r_hist))
        widgets["green_btn"].configure(command=lambda: show_channel_window("Green", g_img, g_hist))
        widgets["blue_btn"].configure(command=lambda: show_channel_window("Blue", b_img, b_hist))

        # ========== POINT PROCESSING BUTTONS ==========
        Button(
            widgets["point_processing_frame"],
            text="Show Grayscale Image",
            command=lambda: show_grayscale_window(widgets)
        ).pack(pady=5)

        Button(
            widgets["point_processing_frame"],
            text="Manual Thresholding",
            command=lambda: show_threshold_window(widgets)
        ).pack(pady=5)

        Button(
            widgets["point_processing_frame"],
            text="Power-Law (Gamma) Transformation",
            command=lambda: show_gamma_window(widgets)
        ).pack(pady=5)

        Button(
            widgets["point_processing_frame"],
            text="Show Negative Image",
            command=lambda: show_negative_window(widgets)
        ).pack(pady=5)

        Button(
            widgets["point_processing_frame"],
            text="Show Histogram Equalization",
            command=lambda: show_hist_eq_window(widgets)
        ).pack(pady=5)

        # ========== STATUS ==========
        widgets["status"].config(
            text=f"? Loaded: {os.path.basename(filepath)}",
            fg="green"
        )

    except Exception as e:
        widgets["status"].config(text=f"? Error: {e}", fg="red")
        import traceback
        traceback.print_exc()


# =====================================================
#   GRAYSCALE IMAGE DISPLAY WINDOW
# =====================================================
def show_grayscale_window(widgets):
    """Displays the grayscale image in a new pop-up window."""
    from tkinter import Toplevel, Label
    from PIL import ImageTk

    if "gray_image" not in widgets or widgets["gray_image"] is None:
        widgets["status"].config(text="? No grayscale image available.")
        return

    top = Toplevel()
    top.title("Grayscale Image")

    img = ImageTk.PhotoImage(widgets["gray_image"])
    Label(top, image=img).pack()
    top.image = img  # Prevent garbage collection
