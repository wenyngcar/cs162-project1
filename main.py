from tkinter import Tk
from ui_components import create_main_ui
from handlers.pcx_loader import open_pcx
from utils.filter_registry import FILTERS

def main():
    # Initialize main window
    root = Tk()
    root.title("PCX File Reader with RGB Histograms")
    root.geometry("1000x800")

    # Create UI components (buttons, image panels, etc.)
    widgets = create_main_ui(root, None)

    # Set open button behavior
    widgets["open_btn"].config(command=lambda: open_pcx(widgets))

    # --- ?? Populate filter dropdown dynamically ---
    menu = widgets["filter_select"]["menu"]
    menu.delete(0, "end")

    for filter_name in FILTERS.keys():
        menu.add_command(
            label=filter_name,
            command=lambda value=filter_name: widgets["filter_select_var"].set(value)
        )

    # --- ? Optional: set a default selection ---
    first_filter = next(iter(FILTERS.keys()), None)
    if first_filter:
        widgets["filter_select_var"].set(first_filter)

    # Run Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()
