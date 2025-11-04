from tkinter import Tk
from ui_components import create_main_ui
from handlers.pcx_loader import open_pcx
from utils.filter_registry import FILTERS
from PIL import ImageTk

def main():
    # Initialize main window
    root = Tk()
    root.title("PCX File Reader with RGB Histograms")
    root.geometry("1000x800")

    # Create UI components (buttons, image panels, etc.)
    widgets = create_main_ui(root, None)

    # Set open button behavior
    widgets["open_btn"].config(command=lambda: open_pcx(widgets))

    # Populate filter dropdown dynamically
    menu = widgets["filter_select"]["menu"]
    menu.delete(0, "end")
    for filter_name in FILTERS.keys():
        menu.add_command(
            label=filter_name,
            command=lambda value=filter_name: widgets["filter_select_var"].set(value)
        )

    # Optional: set a default selection
    first_filter = next(iter(FILTERS.keys()), None)
    if first_filter:
        widgets["filter_select_var"].set(first_filter)

    # Apply filter callback
    def apply_selected_filter():
        selected_filter = widgets["filter_select_var"].get()

        if not selected_filter:
            widgets["status"].config(text="?? No filter selected.")
            return

        filter_entry = FILTERS.get(selected_filter)
        if not filter_entry:
            widgets["status"].config(text=f"?? Filter '{selected_filter}' not found.")
            return

        filter_fn = filter_entry["fn"]

        img_to_filter = widgets.get("current_image")
        if img_to_filter is None:
            widgets["status"].config(text="?? No image loaded for filtering.")
            return

        try:
            # Call the filter function with the current image
            filtered_img = filter_fn(img_to_filter)

            # Store filtered image
            widgets["filtered_image"] = filtered_img

            # Display filtered image
            photo = ImageTk.PhotoImage(filtered_img.resize((400, 400)))
            widgets["filter_result_img"].config(image=photo)
            widgets["filter_result_img"].image = photo  # Keep reference

            widgets["status"].config(text=f"? Applied filter: {selected_filter}")

        except Exception as e:
            widgets["status"].config(text=f"?? Error applying filter: {e}")

    # Connect apply filter button
    widgets["apply_filter_btn"].config(command=apply_selected_filter)

    # Run Tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    main()
