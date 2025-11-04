from tkinter import Toplevel, Label
from PIL import ImageTk
from image_processing import (
    create_threshold_image,
    create_gamma_image,
    create_negative_image,
)
from histogram_equalization import histogram_equalization
from utils.image_utils import render_grayscale_histogram

def show_threshold_window(widgets):
    win = Toplevel()
    win.title("Manual Thresholding")
    gray_img = widgets.get("gray_image")
    if gray_img is None:
        widgets["status"].config(text="No grayscale image available.", fg="red")
        win.destroy()
        return
    bw_img = create_threshold_image(gray_img)
    if bw_img:
        photo = ImageTk.PhotoImage(bw_img.resize((400, 400)))
        lbl = Label(win, image=photo)
        lbl.image = photo
        lbl.pack(pady=10)

def show_gamma_window(widgets):
    win = Toplevel()
    win.title("Power-Law (Gamma) Transformation")
    gray_img = widgets.get("gray_image")
    if gray_img is None:
        widgets["status"].config(text="No grayscale image available.", fg="red")
        win.destroy()
        return
    gamma_img = create_gamma_image(gray_img)
    if gamma_img:
        photo = ImageTk.PhotoImage(gamma_img.resize((400, 400)))
        lbl = Label(win, image=photo)
        lbl.image = photo
        lbl.pack(pady=10)

def show_negative_window(widgets):
    gray_img = widgets.get("gray_image")
    if gray_img is None:
        widgets["status"].config(text="No grayscale image available.", fg="red")
        return
    win = Toplevel()
    win.title("Negative Image")
    negative_img = create_negative_image(gray_img)
    neg_photo = ImageTk.PhotoImage(negative_img.resize((400, 400)))
    lbl = Label(win, image=neg_photo)
    lbl.image = neg_photo
    lbl.pack(pady=5)

def show_hist_eq_window(widgets):
    gray_img = widgets.get("gray_image")
    if gray_img is None:
        widgets["status"].config(text="No grayscale image available.", fg="red")
        return
    win = Toplevel()
    win.title("Histogram Equalization")
    equalized_img, _ = histogram_equalization(gray_img)
    orig_hist_img = render_grayscale_histogram(gray_img)
    eq_hist_img = render_grayscale_histogram(equalized_img)
    orig_photo = ImageTk.PhotoImage(gray_img.resize((400, 400)))
    eq_photo = ImageTk.PhotoImage(equalized_img.resize((400, 400)))
    orig_hist_photo = ImageTk.PhotoImage(orig_hist_img.resize((400, 300)))
    eq_hist_photo = ImageTk.PhotoImage(eq_hist_img.resize((400, 300)))

    Label(win, text="Original Grayscale").grid(row=0, column=0, padx=10)
    Label(win, text="Equalized Image").grid(row=0, column=1, padx=10)
    Label(win, image=orig_photo).grid(row=1, column=0, padx=10, pady=5)
    Label(win, image=eq_photo).grid(row=1, column=1, padx=10, pady=5)
    Label(win, text="Original Histogram").grid(row=2, column=0, padx=10)
    Label(win, text="Equalized Histogram").grid(row=2, column=1, padx=10)
    Label(win, image=orig_hist_photo).grid(row=3, column=0, padx=10, pady=5)
    Label(win, image=eq_hist_photo).grid(row=3, column=1, padx=10, pady=5)

    # keep references
    win.orig_photo = orig_photo
    win.eq_photo = eq_photo
    win.orig_hist_photo = orig_hist_photo
    win.eq_hist_photo = eq_hist_photo
