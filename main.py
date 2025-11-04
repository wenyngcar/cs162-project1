from tkinter import Tk, simpledialog
from ui_components import create_main_ui
from handlers.pcx_loader import open_pcx
from utils.filter_registry import FILTERS

def main():
    root = Tk()
    root.title("PCX File Reader with RGB Histograms")
    root.geometry("1000x800")

    widgets = create_main_ui(root, None)
    widgets["open_btn"].config(command=lambda: open_pcx(widgets))

    # ========== FILTER APPLICATION ==========
    def prompt_params(params_spec):
        """Prompt user for filter parameters."""
        params = {}
        for name, param_type, default, constraints in params_spec:
            if param_type == "int":
                val = simpledialog.askinteger("Parameter", f"Enter {name} (default {default}):", initialvalue=default)
            elif param_type == "float":
                val = simpledialog.askfloat("Parameter", f"Enter {name} (default {default}):", initialvalue=default)
            else:
                val = default
            params[name] = val
        return params

    def apply_selected_filter():
        """Apply selected filter to the current image."""
        if "current_image" not in widgets or widgets["current_image"] is None:
            widgets["status"].config(text="?? No image loaded. Please open a PCX file first.")
            return

        selected_filter = widgets["filter_var"].get()
        if selected_filter not in FILTERS:
            widgets["status"].config(text="?? Invalid filter selected.")
            return

        filter_info = FILTERS[selected_filter]
        params = prompt_params(filter_info.get("params", []))

        # Apply the selected filter
        filter_fn = filter_info["fn"]
        try:
            filtered_img = filter_fn(widgets["current_image"], **params)
            widgets["filtered_image"] = filtered_img
            widgets["status"].config(text=f"? Applied filter: {selected_filter}")
        except Exception as e:
            widgets["status"].config(text=f"? Error applying filter: {e}")

    # Connect filter apply button
    if "apply_filter_btn" in widgets:
        widgets["apply_filter_btn"].configure(command=apply_selected_filter)

    # Run main loop
    root.mainloop()


if __name__ == "__main__":
    main()
