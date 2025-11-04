from tkinter import Tk, filedialog, Label
from PIL import Image, ImageDraw, ImageTk
import os, io, matplotlib.pyplot as plt
from pcx_reader import read_pcx_header, read_pcx_palette, decompress_rle
from image_processing import create_grayscale_image, create_negative_image
from ui_components import create_main_ui
from image_processing import create_threshold_image
from histogram_equalization import histogram_equalization
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
        original_img_disp = original_img.copy()
        original_img_disp.thumbnail((400, 400))
        original_photo = ImageTk.PhotoImage(original_img_disp)
        widgets["original_img"].config(image=original_photo)
        widgets["original_img"].image = original_photo
        
        # Calculate scale factor for click coordinates
        scale_x = original_img.width / original_img_disp.width
        scale_y = original_img.height / original_img_disp.height
        
        # Add click handler to show RGB values
        def show_rgb_values(event):
            # Convert click coordinates to original image coordinates
            x = int(event.x * scale_x)
            y = int(event.y * scale_y)
            
            # Check if coordinates are within bounds
            if 0 <= x < original_img.width and 0 <= y < original_img.height:
                rgb = original_img.getpixel((x, y))
                widgets["rgb_info"].config(
                    text=f"Position: ({x}, {y}) | RGB: {rgb} | R={rgb[0]}, G={rgb[1]}, B={rgb[2]}"
                )
            else:
                widgets["rgb_info"].config(text="Click inside the image to see RGB values")
        
        # Bind click event
        widgets["original_img"].bind("<Button-1>", show_rgb_values)
        
        # Image

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

        # Grayscale + histogram
        gray_img = create_grayscale_image(img)
        gray_disp = gray_img.copy()
        gray_disp.thumbnail((400, 400))
        gray_photo = ImageTk.PhotoImage(gray_disp)
        widgets["gray"].config(image=gray_photo)
        widgets["gray"].image = gray_photo

        # Negative Image
        neg_img = create_negative_image(gray_img)
        neg_disp = neg_img.copy()
        neg_disp.thumbnail((400, 400))
        neg_photo = ImageTk.PhotoImage(neg_disp)

        # Create a new label for displaying the negative image
        if "negative" not in widgets:
            from tkinter import Label
            neg_label_title = Label(widgets["gray"].master.master, text="Negative Image:", font=("Arial", 11, "bold"))
            neg_label_title.pack(anchor="w")
            neg_label = Label(widgets["gray"].master.master, bg="white", relief="sunken")
            neg_label.pack(pady=10)
            widgets["negative"] = neg_label
        

        # --- Black/White via Manual Thresholding ---
        bw_img = create_threshold_image(gray_img)
        if bw_img:
            bw_disp = bw_img.copy()
            bw_disp.thumbnail((400, 400))
            bw_photo = ImageTk.PhotoImage(bw_disp)

            if "bw" not in widgets:
                from tkinter import Label
                bw_label_title = Label(widgets["gray"].master.master, text="Black/White (Manual Thresholding):", font=("Arial", 11, "bold"))
                bw_label_title.pack(anchor="w")
                bw_label = Label(widgets["gray"].master.master, bg="white", relief="sunken")
                bw_label.pack(pady=10)
                widgets["bw"] = bw_label

            widgets["bw"].config(image=bw_photo)
            widgets["bw"].image = bw_photo


# --- Power-Law (Gamma) Transformation ---
        from image_processing import create_gamma_image
        gamma_img = create_gamma_image(gray_img)
        if gamma_img:
            gamma_disp = gamma_img.copy()
            gamma_disp.thumbnail((400, 400))
            gamma_photo = ImageTk.PhotoImage(gamma_disp)

            if "gamma" not in widgets:
                gamma_label_title = Label(widgets["gray"].master.master, text="Power-Law (Gamma) Transformation:", font=("Arial", 11, "bold"))
                gamma_label_title.pack(anchor="w")
                gamma_label = Label(widgets["gray"].master.master, bg="white", relief="sunken")
                gamma_label.pack(pady=10)
                widgets["gamma"] = gamma_label

            widgets["gamma"].config(image=gamma_photo)
            widgets["gamma"].image = gamma_photo


        widgets["negative"].config(image=neg_photo)
        widgets["negative"].image = neg_photo

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

    root.mainloop()

if __name__ == "__main__":
    main()
