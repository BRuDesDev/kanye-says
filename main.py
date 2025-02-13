import tkinter as tk

import emoji
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from PIL import Image, ImageTk, ImageOps

is_flipped = False
history = []
scores = {}
last_quote = ""
history_visible = False  # track the toggle

HISTORY_WIDTH = 400  # width of the history drawer
HISTORY_HEIGHT = 600  # you can tweak or dynamically match root's height

# Create emojis
history_toggle = emoji.emojize(":open_file_folder:")
thumbs_up = emoji.emojize(":thumbs_up:")
thumbs_down = emoji.emojize(":thumbs_down:")


def get_quote(_event=None):
    """Use the "Kanye Rest" API to scrape tweets from Kanye West's Twitter account"""
    global last_quote
    response = requests.get("https://api.kanye.rest")
    response.raise_for_status()
    data = response.json()
    quote = data["quote"]

    last_quote = quote
    history.append(quote)
    scores[quote] = "neutral"  # default rating

    canvas.itemconfig(quote_text, text=quote)
    refresh_history()


def flip_kanye(_event=None):
    """
    Mirror (flip horizontally) the image of Kanye's head each time the user requests a new tweet
    Gives appearance of animation
    """
    global is_flipped, kanye_raw, kanye_img
    if not is_flipped:
        flipped = ImageOps.mirror(kanye_raw)
        kanye_img = ImageTk.PhotoImage(flipped)
        is_flipped = True
    else:
        kanye_img = ImageTk.PhotoImage(kanye_raw)
        is_flipped = False

    canvas.itemconfig(kanye_item, image=kanye_img)


def upvote_quote(_event=None):
    """Function to handle upvotes of quotes in History window"""
    if last_quote:
        scores[last_quote] = "up"
        refresh_history()


def downvote_quote(_event=None):
    """Function to handle downvotes of quotes in History window"""
    if last_quote:
        scores[last_quote] = "down"
        refresh_history()


def refresh_history():
    """Clear and re-populate the history listbox"""
    if listbox.size() > 0:
        listbox.delete(0, tk.END)

    for q in history:
        status = scores.get(q, "neutral")
        if status == "up":
            listbox.insert(tk.END, f"{q} {thumbs_up}")
        elif status == "down":
            listbox.insert(tk.END, f"{q}  {thumbs_down}")
        else:
            listbox.insert(tk.END, q)
        # Insert a separator line
        listbox.insert(tk.END, "-" * 50)


def toggle_history(_event=None):
    """
    If hidden, move the history window so that its left border
    aligns with the main window’s right border.
    If visible, move it off-screen
    """
    global history_visible
    if history_visible:
        hide_history_window()
        history_visible = False
    else:
        show_history_window()
        history_visible = True


def show_history_window():
    """
    Calculate the root windows geometry
    Position the top-level window so its left edge aligns with the main window's right edge.
    """
    window.update_idletasks()  # ensure geometry info is correct

    # Root window coordinates
    root_x = window.winfo_rootx()
    root_y = window.winfo_rooty()
    root_w = window.winfo_width()
    root_h = window.winfo_height()

    # Position the history window so that its left border touches the root's right border
    # e.g. top-left corner at (root_x + root_w, root_y)
    history_geometry = f"{HISTORY_WIDTH}x{HISTORY_HEIGHT}+{root_x + root_w}+{root_y}"
    history_window.geometry(history_geometry)
    # Position History window behind root
    history_window.lower(window)
    # make sure it's not hidden
    history_window.deiconify()
    refresh_history()


def hide_history_window():
    """Hide the history window by moving it off-screen"""

    # Move it way off-screen so the user can't see it.
    # comment out the above lower(...) if you want to physically move it
    # window.update_idletasks()
    # root_x = window.winfo_rootx()
    # root_y = window.winfo_rooty()
    # offscreen_x = root_x + window.winfo_width() + 2000  # 2000 px to the right
    # offscreen_geometry = f"{HISTORY_WIDTH}x{HISTORY_HEIGHT}+{offscreen_x}+{root_y}"
    # history_window.geometry(offscreen_geometry)

    # Just withdraw it (completely hide).
    history_window.withdraw()


# ---------- Create main window ----------
style = ttk.Style(theme="superhero")
window = style.master
window.title("Kanye Says...")

# A frame to hold everything
main_frame = ttk.Frame(window, padding=10)
main_frame.pack(fill='both', expand=True)

# Canvas
canvas = tk.Canvas(main_frame, highlightthickness=0)
canvas.pack(fill='both', expand=True)

# Background image
try:
    bg_img_raw = Image.open("images/quote-box.png")
except:
    # fallback if image not found
    import io
    import base64

    # create a small placeholder
    bg_img_raw = Image.new("RGB", (400, 300), color="white")

bg_width, bg_height = bg_img_raw.size
bg_img = ImageTk.PhotoImage(bg_img_raw)

canvas.config(width=bg_width + 20, height=bg_height + 20)
canvas.create_image(bg_width // 2, bg_height // 2, image=bg_img)

# Quote placeholder text
quote_text = canvas.create_text(
    bg_width // 2,
    bg_height // 2,
    text="Click Kanye's face to see some genius...",
    width=300,
    font=("Noteworthy", 20, "normal"),
    fill="black",
    anchor="center"
)

# Kanye image
try:
    kanye_raw = Image.open("images/kanye.png")
except:
    kanye_raw = Image.new("RGB", (100, 100), color="gray")

kanye_img = ImageTk.PhotoImage(kanye_raw)
# Resize image and add multiple callbacks when clicked
kanye_item = canvas.create_image(bg_width // 2, bg_height - 70, image=kanye_img)
canvas.tag_bind(kanye_item, "<Button-1>", flip_kanye)
canvas.tag_bind(kanye_item, "<Button-1>", get_quote, add="+")

# Thumbs up/down
thumbs_up_item = canvas.create_text(
    40, bg_height - 30,
    text=thumbs_up, font=("Arial", 25), fill="green"
)
canvas.tag_bind(thumbs_up_item, "<Button-1>", upvote_quote)

thumbs_down_item = canvas.create_text(
    bg_width - 40, bg_height - 30,
    text=thumbs_down, font=("Arial", 25), fill="red"
)
canvas.tag_bind(thumbs_down_item, "<Button-1>", downvote_quote)

# History icon (toggle) in top-right
history_icon = canvas.create_text(
    bg_width - 20, 20,
    text=history_toggle, font=("Arial", 40), fill="blue"
)
canvas.tag_bind(history_icon, "<Button-1>", toggle_history)

# -------- Create History Window (Toplevel) ----------
history_window = ttk.Toplevel(window)
history_window.title("History")
history_window.withdraw()  # start hidden so we can place it behind or off-screen
history_window.protocol("WM_DELETE_WINDOW", lambda: None)  # disable 'X' for now, or handle gracefully

# Frame inside the Toplevel
list_frame = ttk.Frame(history_window, padding=10)
list_frame.pack(fill='both', expand=True)

scrollbar = ttk.Scrollbar(list_frame, orient='vertical')
listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 11), background="white")
scrollbar.config(command=listbox.yview)
listbox.pack(side='left', fill='both', expand=True)
scrollbar.pack(side='right', fill='y')

# Start main loop
window.mainloop()
