from tkinter import *

def create_main_ui(root, open_callback):
    """Builds all UI elements and returns dictionary of widgets."""
    Button(root, text="Open PCX File", command=open_callback,
           bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
           padx=20, pady=5).pack(pady=10)

    status_label = Label(root, text="No file loaded", fg="gray")
    status_label.pack()

    # Scrollable container
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

    # Main image
    Label(scrollable_frame, text="Decompressed Image:", font=("Arial", 11, "bold")).pack(anchor=W)
    img_label = Label(scrollable_frame, bg="white", relief=SUNKEN)
    img_label.pack(pady=10)

    # RGB channel + histogram layout
    channel_labels = {}
    histogram_labels = {}
    for title, key in zip(["Red Channel", "Green Channel", "Blue Channel"], ["r", "g", "b"]):
        Label(scrollable_frame, text=title, font=("Arial", 11, "bold")).pack(anchor=W)
        frame = Frame(scrollable_frame)
        frame.pack(pady=5)
        channel_labels[key] = Label(frame, bg="white", relief=SUNKEN)
        channel_labels[key].pack(side=LEFT, padx=10)
        histogram_labels[key] = Label(frame, bg="white", relief=SUNKEN)
        histogram_labels[key].pack(side=LEFT, padx=10)

    # Grayscale + histogram
    Label(scrollable_frame, text="Grayscale Image:", font=("Arial", 11, "bold")).pack(anchor=W)
    gray_frame = Frame(scrollable_frame)
    gray_frame.pack(pady=10)
    gray_label = Label(gray_frame, bg="white", relief=SUNKEN)
    gray_label.pack(side=LEFT, padx=10)
    gray_hist_label = Label(gray_frame, bg="white", relief=SUNKEN)
    gray_hist_label.pack(side=LEFT, padx=10)

    # Mouse scroll
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    return {
        "status": status_label,
        "header": header_text,
        "palette": palette_label,
        "img": img_label,
        "r": channel_labels["r"], "g": channel_labels["g"], "b": channel_labels["b"],
        "r_hist": histogram_labels["r"], "g_hist": histogram_labels["g"], "b_hist": histogram_labels["b"],
        "gray": gray_label, "gray_hist": gray_hist_label
    }
