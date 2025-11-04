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

    # Original Image (clickable for RGB values)
    Label(scrollable_frame, text="Original Image (click to see RGB values):", font=("Arial", 11, "bold")).pack(anchor=W)
    original_img_label = Label(scrollable_frame, bg="white", relief=SUNKEN, cursor="crosshair")
    original_img_label.pack(pady=5)
    rgb_info_label = Label(scrollable_frame, text="", font=("Courier", 10), fg="blue")
    rgb_info_label.pack()

    # Palette
    Label(scrollable_frame, text="Color Palette:", font=("Arial", 11, "bold")).pack(anchor=W)
    palette_label = Label(scrollable_frame, bg="white", relief=SUNKEN)
    palette_label.pack(pady=5)

    # Main image
    Label(scrollable_frame, text="Decompressed Image:", font=("Arial", 11, "bold")).pack(anchor=W)
    img_label = Label(scrollable_frame, bg="white", relief=SUNKEN)
    img_label.pack(pady=10)

    # RGB Channels
    Label(scrollable_frame, text="RGB Channels:", font=("Arial", 11, "bold")).pack(anchor=W)
    rgb_frame = Frame(scrollable_frame)
    rgb_frame.pack(pady=10)
    
    # Red channel
    red_frame = Frame(rgb_frame)
    red_frame.pack(side=LEFT, padx=5)
    Label(red_frame, text="Red Channel", font=("Arial", 9, "bold"), fg="red").pack()
    red_label = Label(red_frame, bg="white", relief=SUNKEN)
    red_label.pack()
    red_hist_label = Label(red_frame, bg="white", relief=SUNKEN)
    red_hist_label.pack(pady=2)
    
    # Green channel
    green_frame = Frame(rgb_frame)
    green_frame.pack(side=LEFT, padx=5)
    Label(green_frame, text="Green Channel", font=("Arial", 9, "bold"), fg="green").pack()
    green_label = Label(green_frame, bg="white", relief=SUNKEN)
    green_label.pack()
    green_hist_label = Label(green_frame, bg="white", relief=SUNKEN)
    green_hist_label.pack(pady=2)
    
    # Blue channel
    blue_frame = Frame(rgb_frame)
    blue_frame.pack(side=LEFT, padx=5)
    Label(blue_frame, text="Blue Channel", font=("Arial", 9, "bold"), fg="blue").pack()
    blue_label = Label(blue_frame, bg="white", relief=SUNKEN)
    blue_label.pack()
    blue_hist_label = Label(blue_frame, bg="white", relief=SUNKEN)
    blue_hist_label.pack(pady=2)

    # Grayscale + histogram
    Label(scrollable_frame, text="Grayscale Image:", font=("Arial", 11, "bold")).pack(anchor=W)
    gray_frame = Frame(scrollable_frame)
    gray_frame.pack(pady=10)
    gray_label = Label(gray_frame, bg="white", relief=SUNKEN)
    gray_label.pack(side=LEFT, padx=10)
    gray_hist_label = Label(gray_frame, bg="white", relief=SUNKEN)
    gray_hist_label.pack(side=LEFT, padx=10)

    # Container for point processing methods (negative, threshold, gamma, histogram equalization)
    # This will be populated dynamically when an image is loaded
    point_processing_frame = Frame(scrollable_frame)
    point_processing_frame.pack(pady=10, fill=X)

    # Smoothing Filters section (dropdown + single apply + single result) - AT THE BOTTOM
    Label(scrollable_frame, text="Smoothing Filters:", font=("Arial", 11, "bold")).pack(anchor=W)
    filters_frame = Frame(scrollable_frame)
    filters_frame.pack(pady=10, fill=X)

    from tkinter import StringVar, OptionMenu
    selector_row = Frame(filters_frame)
    selector_row.pack(anchor=W, pady=2)
    Label(selector_row, text="Filter:").pack(side=LEFT, padx=(0, 6))
    filter_select_var = StringVar()
    filter_select = OptionMenu(selector_row, filter_select_var, "")
    filter_select.config(width=18)
    filter_select.pack(side=LEFT)
    apply_filter_btn = Button(selector_row, text="Apply Filter")
    apply_filter_btn.pack(side=LEFT, padx=8)

    result_frame = Frame(filters_frame)
    result_frame.pack(pady=8, fill=X)
    Label(result_frame, text="Filter Result", font=("Arial", 9, "bold")).pack(anchor=W)
    filter_result_img = Label(result_frame, bg="white", relief=SUNKEN)
    filter_result_img.pack()

    # Mouse scroll
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    return {
        "status": status_label,
        "header": header_text,
        "original_img": original_img_label,
        "rgb_info": rgb_info_label,
        "palette": palette_label,
        "img": img_label,
        "red": red_label, "red_hist": red_hist_label,
        "green": green_label, "green_hist": green_hist_label,
        "blue": blue_label, "blue_hist": blue_hist_label,
        "gray": gray_label, "gray_hist": gray_hist_label,
        "point_processing_frame": point_processing_frame,
        "filter_select_var": filter_select_var,
        "filter_select": filter_select,
        "apply_filter_btn": apply_filter_btn,
        "filter_result_img": filter_result_img
    }
