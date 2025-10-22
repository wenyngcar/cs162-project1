from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import os

def read_pcx_header(filepath):
    """Read and parse the 128-byte PCX file header."""
    with open(filepath, 'rb') as f:
        h = f.read(128)
        header = {
            'Manufacturer': h[0],
            'Version': h[1],
            'Encoding': h[2],
            'BitsPerPixel': h[3],
            'Xmin': int.from_bytes(h[4:6], 'little'),
            'Ymin': int.from_bytes(h[6:8], 'little'),
            'Xmax': int.from_bytes(h[8:10], 'little'),
            'Ymax': int.from_bytes(h[10:12], 'little'),
            'HDPI': int.from_bytes(h[12:14], 'little'),
            'VDPI': int.from_bytes(h[14:16], 'little'),
            'NPlanes': h[65],
            'BytesPerLine': int.from_bytes(h[66:68], 'little'),
        }
        header['Width'] = header['Xmax'] - header['Xmin'] + 1
        header['Height'] = header['Ymax'] - header['Ymin'] + 1
        return header


def read_pcx_palette(filepath):
    """Read the 256-color palette stored at the end of 8-bit PCX files."""
    with open(filepath, 'rb') as f:
        f.seek(-769, os.SEEK_END)
        marker = f.read(1)
        data = f.read(768)
        palette = [(data[i], data[i+1], data[i+2]) for i in range(0, 768, 3)]
        return palette


def decompress_rle(filepath):
    """Manually decode PCX pixel data using Run-Length Encoding (RLE)."""
    with open(filepath, 'rb') as f:
        f.seek(128)
        pixel_data = []
        file_size = os.path.getsize(filepath)
        end_pos = file_size - 769
        while f.tell() < end_pos:
            byte = f.read(1)
            if not byte:
                break
            val = byte[0]
            if val >= 0xC0:
                count = val & 0x3F
                data_byte = f.read(1)[0]
                pixel_data.extend([data_byte] * count)
            else:
                pixel_data.append(val)
        return pixel_data


# ----------------------------- NEW FUNCTION -----------------------------
def show_rgb_channels(img):
    """Split the given image into R, G, and B channels and display them."""
    r, g, b = img.split()

    # Convert grayscale channels back into RGB images for visualization
    r_img = Image.merge("RGB", (r, Image.new("L", r.size), Image.new("L", r.size)))
    g_img = Image.merge("RGB", (Image.new("L", g.size), g, Image.new("L", g.size)))
    b_img = Image.merge("RGB", (Image.new("L", b.size), Image.new("L", b.size), b))

    # Create a new window to show channels
    win = Toplevel()
    win.title("RGB Channels")

    # Helper function to add image with label
    def add_image(title, image):
        image = image.resize((200, 200))
        photo = ImageTk.PhotoImage(image)
        frame = Frame(win)
        frame.pack(side=LEFT, padx=10, pady=10)
        Label(frame, text=title, font=("Arial", 11, "bold")).pack()
        lbl = Label(frame, image=photo)
        lbl.image = photo
        lbl.pack()

    add_image("Red Channel", r_img)
    add_image("Green Channel", g_img)
    add_image("Blue Channel", b_img)


# ----------------------------- GUI FILE HANDLER -----------------------------
def open_pcx():
    """Open a PCX file, decode it, and display its contents in the GUI."""
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
        expected_size = width * height

        if len(pixels) < expected_size:
            raise ValueError("Decompressed pixel data smaller than expected.")

        img = Image.new('RGB', (width, height))
        img.putdata([palette[p] for p in pixels[:expected_size]])

        # Save current image globally for channel display
        global current_image
        current_image = img.copy()

        # Display Header Information 
        info_lines = [
            f"Manufacturer: {header['Manufacturer']}",
            f"Version: {header['Version']}",
            f"Encoding: {header['Encoding']}",
            f"Bits per Pixel: {header['BitsPerPixel']}",
            f"Dimensions: {width}x{height}",
            f"Color Planes: {header['NPlanes']}",
            f"Bytes per Line: {header['BytesPerLine']}",
        ]
        header_text.delete(1.0, END)
        header_text.insert(1.0, '\n'.join(info_lines))

        # Display Color Palette 
        cols = 16
        swatch = 20
        pal_img = Image.new('RGB', (cols * swatch, (len(palette)//cols) * swatch), 'white')
        draw = ImageDraw.Draw(pal_img)
        for i, color in enumerate(palette):
            x = (i % cols) * swatch
            y = (i // cols) * swatch
            draw.rectangle([x, y, x + swatch - 1, y + swatch - 1], fill=color, outline='gray')

        pal_photo = ImageTk.PhotoImage(pal_img)
        palette_label.config(image=pal_photo, text="")
        palette_label.image = pal_photo

        # Display Decompressed Image 
        img.thumbnail((400, 400))
        photo = ImageTk.PhotoImage(img)
        img_label.config(image=photo)
        img_label.image = photo

        # Enable the "Show RGB Channels" button
        rgb_button.config(state=NORMAL)

        status_label.config(text=f"Loaded: {os.path.basename(filepath)}", fg="green")

    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")
        import traceback
        traceback.print_exc()


# ----------------------------- GUI SETUP -----------------------------
def main():
    global root, status_label, header_text, palette_label, img_label, rgb_button, current_image

    current_image = None

    root = Tk()
    root.title("PCX File Reader (Manual RLE)")
    root.geometry("1000x600")

    Button(root, text="Open PCX File", command=open_pcx, bg="#4CAF50", fg="white",
           font=("Arial", 12, "bold"), padx=20, pady=5).pack(pady=10)

    # NEW BUTTON for RGB channels
    rgb_button = Button(root, text="Show RGB Channels", command=lambda: show_rgb_channels(current_image),
                        bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
                        padx=10, pady=5, state=DISABLED)
    rgb_button.pack(pady=5)

    status_label = Label(root, text="No file loaded", fg="gray")
    status_label.pack()

    content = Frame(root)
    content.pack(fill=BOTH, expand=True, padx=10, pady=10)

    left = Frame(content)
    left.pack(side=LEFT, fill=BOTH, expand=True)
    Label(left, text="Header Information:", font=("Arial", 11, "bold")).pack(anchor=W)
    header_text = Text(left, width=40, height=15, font=("Courier", 9))
    header_text.pack(fill=BOTH, expand=True, pady=5)

    middle = Frame(content)
    middle.pack(side=LEFT, padx=5)
    Label(middle, text="Color Palette:", font=("Arial", 11, "bold")).pack(anchor=W)
    palette_label = Label(middle, bg="white", relief=SUNKEN)
    palette_label.pack(pady=5)

    right = Frame(content)
    right.pack(side=RIGHT, fill=BOTH, expand=True)
    Label(right, text="Image Display:", font=("Arial", 11, "bold")).pack(anchor=W)
    img_label = Label(right, bg="white", relief=SUNKEN)
    img_label.pack(fill=BOTH, expand=True, pady=5)

    root.mainloop()


# PROGRAM ENTRY POINT 
if __name__ == "__main__":
    main()
