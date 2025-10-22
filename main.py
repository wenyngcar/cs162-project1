from tkinter import Tk, filedialog, Label
from PIL import Image, ImageDraw, ImageTk
import os, io, matplotlib.pyplot as plt

from pcx_reader import read_pcx_header, read_pcx_palette, decompress_rle
from image_processing import create_rgb_channel_images, create_histogram, create_grayscale_image
from ui_components import create_main_ui

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

        # Palette preview
        cols, swatch = 16, 20
        pal_img = Image.new('RGB', (cols * swatch, (len(palette)//cols) * swatch), 'white')
        draw = ImageDraw.Draw(pal_img)
        for i, color in enumerate(palette):
            x, y = (i % cols) * swatch, (i // cols) * swatch
            draw.rectangle([x, y, x + swatch - 1, y + swatch - 1], fill=color, outline='gray')
        pal_photo = ImageTk.PhotoImage(pal_img)
        widgets["palette"].config(image=pal_photo)
        widgets["palette"].image = pal_photo

        # Main image
        img_disp = img.copy()
        img_disp.thumbnail((400, 400))
        photo = ImageTk.PhotoImage(img_disp)
        widgets["img"].config(image=photo)
        widgets["img"].image = photo

        # RGB + histograms
        r_img, g_img, b_img, (r_ch, g_ch, b_ch) = create_rgb_channel_images(img)
        for color, ch_img, ch_gray in zip(
            ["r", "g", "b"],
            [r_img, g_img, b_img],
            [r_ch, g_ch, b_ch]
        ):
            ch_img.thumbnail((250, 250))
            photo = ImageTk.PhotoImage(ch_img)
            widgets[color].config(image=photo)
            widgets[color].image = photo

            hist_img = create_histogram(ch_gray, color)
            hist_img.thumbnail((250, 250))
            hist_photo = ImageTk.PhotoImage(hist_img)
            widgets[f"{color}_hist"].config(image=hist_photo)
            widgets[f"{color}_hist"].image = hist_photo

        # Grayscale + histogram
        gray_img = create_grayscale_image(img)
        gray_disp = gray_img.copy()
        gray_disp.thumbnail((400, 400))
        gray_photo = ImageTk.PhotoImage(gray_disp)
        widgets["gray"].config(image=gray_photo)
        widgets["gray"].image = gray_photo

        gray_hist = gray_img.histogram()
        plt.figure(figsize=(4, 3))
        plt.bar(range(256), gray_hist, color='gray')
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        gray_hist_img = Image.open(buf)
        gray_hist_img.thumbnail((400, 400))
        gray_hist_photo = ImageTk.PhotoImage(gray_hist_img)
        widgets["gray_hist"].config(image=gray_hist_photo)
        widgets["gray_hist"].image = gray_hist_photo

        widgets["status"].config(text=f"Loaded: {os.path.basename(filepath)}", fg="green")

    except Exception as e:
        widgets["status"].config(text=f"Error: {e}", fg="red")
        import traceback
        traceback.print_exc()

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

    root.mainloop()

if __name__ == "__main__":
    main()
