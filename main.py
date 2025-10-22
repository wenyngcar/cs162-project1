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

def create_rgb_channel_images(img):
    """Return three images showing the Red, Green, and Blue channels separately."""
    r, g, b = img.split()
    r_img = Image.merge("RGB", (r, Image.new("L", r.size), Image.new("L", r.size)))
    g_img = Image.merge("RGB", (Image.new("L", g.size), g, Image.new("L", g.size)))
    b_img = Image.merge("RGB", (Image.new("L", b.size), Image.new("L", b.size), b))
    return r_img, g_img, b_img

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

        # Header Info
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

        # Palette
        cols = 16
        swatch = 20
        pal_img = Image.new('RGB', (cols * swatch, (len(palette)//cols) * swatch), 'white')
        draw = ImageDraw.Draw(pal_img)
        for i, color in enumerate(palette):
            x = (i % cols) * swatch
            y = (i // cols) * swatch
            draw.rectangle([x, y, x + swatch - 1, y + swatch - 1], fill=color, outline='gray')
        pal_photo = ImageTk.PhotoImage(pal_img)
        palette_label.config(image=pal_photo)
        palette_label.image = pal_photo

        # Main Image
        img_disp = img.copy()
        img_disp.thumbnail((400, 400))
        photo = ImageTk.PhotoImage(img_disp)
        img_label.config(image=photo)
        img_label.image = photo

        # RGB Channels
        r_img, g_img, b_img = create_rgb_channel_images(img)
        for channel_img in (r_img, g_img, b_img):
            channel_img.thumbnail((250, 250))
        r_photo = ImageTk.PhotoImage(r_img)
        g_photo = ImageTk.PhotoImage(g_img)
        b_photo = ImageTk.PhotoImage(b_img)
        r_label.config(image=r_photo)
        r_label.image = r_photo
        g_label.config(image=g_photo)
        g_label.image = g_photo
        b_label.config(image=b_photo)
        b_label.image = b_photo

        status_label.config(text=f"Loaded: {os.path.basename(filepath)}", fg="green")

    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")
        import traceback
        traceback.print_exc()

def main():
    global root, status_label, header_text, palette_label, img_label
    global r_label, g_label, b_label

    root = Tk()
    root.title("PCX File Reader (Scrollable Vertical Layout)")
    root.geometry("900x700")

    Button(root, text="Open PCX File", command=open_pcx,
           bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
           padx=20, pady=5).pack(pady=10)

    status_label = Label(root, text="No file loaded", fg="gray")
    status_label.pack()

    # Scrollable Canvas setup
    container = Frame(root)
    container.pack(fill=BOTH, expand=True)

    canvas = Canvas(container)
    scrollbar = Scrollbar(container, orient=VERTICAL, command=canvas.yview)
    scrollable_frame = Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)

    # Header
    Label(scrollable_frame, text="Header Information:", font=("Arial", 11, "bold")).pack(anchor=W)
    header_text = Text(scrollable_frame, width=70, height=10, font=("Courier", 9))
    header_text.pack(pady=5)

    # Palette
    Label(scrollable_frame, text="Color Palette:", font=("Arial", 11, "bold")).pack(anchor=W)
    palette_label = Label(scrollable_frame, bg="white", relief=SUNKEN)
    palette_label.pack(pady=5)

    # Main Image
    Label(scrollable_frame, text="Decompressed Image:", font=("Arial", 11, "bold")).pack(anchor=W)
    img_label = Label(scrollable_frame, bg="white", relief=SUNKEN)
    img_label.pack(pady=10)

    # RGB Channels
    Label(scrollable_frame, text="RGB Channels:", font=("Arial", 11, "bold")).pack(anchor=W)
    r_label = Label(scrollable_frame, bg="white", relief=SUNKEN)
    r_label.pack(pady=5)
    Label(scrollable_frame, text="Red Channel", font=("Arial", 10, "bold")).pack()

    g_label = Label(scrollable_frame, bg="white", relief=SUNKEN)
    g_label.pack(pady=5)
    Label(scrollable_frame, text="Green Channel", font=("Arial", 10, "bold")).pack()

    b_label = Label(scrollable_frame, bg="white", relief=SUNKEN)
    b_label.pack(pady=5)
    Label(scrollable_frame, text="Blue Channel", font=("Arial", 10, "bold")).pack()

    # Allow mousewheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    root.mainloop()

if __name__ == "__main__":
    main()
