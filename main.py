import requests
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk, ImageOps

is_flipped = False


def get_quote(_event=None):
    """
    Use Requests library to access the kanye rest api and scrape individual tweets
    """
    response = requests.get("https://api.kanye.rest")
    response.raise_for_status()
    data = response.json()
    quote = data["quote"]
    # Update the text on the canvas
    canvas.itemconfig(quote_text, text=quote)


def flip_kanye(_event=None):
    """
    Function to flip the image of Kanye's head (mirrored horizontally)
    """
    global is_flipped
    global kanye_raw, kanye_img, kanye_item, canvas

    # Flip the raw image horizontally
    if not is_flipped:
        flipped = ImageOps.mirror(kanye_raw)
        kanye_img = ImageTk.PhotoImage(flipped)
        is_flipped = True
    else:
        # Flip it back to original
        kanye_img = ImageTk.PhotoImage(kanye_raw)
        is_flipped = False

    # Update the image item on the canvas
    canvas.itemconfig(kanye_item, image=kanye_img)


# Create main window
style = ttk.Style(theme="superhero")  # Use ttkbootstrap superhero theme
window = style.master
window.title("Kanye Says...")

# A frame to hold everything
main_frame = ttk.Frame(window, padding=10)
main_frame.pack(fill=BOTH, expand=YES)

# Load the background image with Pillow
bg_img_raw = Image.open("images/quote-box.png")

# Scale it to 130% of original size
new_width = int(bg_img_raw.width * 1.3)
new_height = int(bg_img_raw.height * 1.3)

# Resize the image using the new width and height
bg_img_raw = bg_img_raw.resize((new_width, new_height))
bg_img = ImageTk.PhotoImage(bg_img_raw)
bg_width, bg_height = bg_img_raw.size

# Create a canvas 10 px bigger in each direction
canvas = ttk.Canvas(main_frame, width=new_width + 10, height=new_height + 10)
canvas.pack()

# Place the quote box at the center of the canvas
canvas.create_image(bg_width // 2, bg_height // 2, image=bg_img)

# Create the text item
quote_text = canvas.create_text(
    bg_width // 2,
    bg_height // 2,  # Adjust so text is inside the quote bubble
    text="Click Kanye’s face to see some genius...",
    width=300,  # Let text wrap if needed
    font=("Noteworthy", 20, "normal"),
    fill="black",
    anchor="center"
)

# Load Kanye’s head with transparency
kanye_raw = Image.open("images/kanye.png")
kanye_img = ImageTk.PhotoImage(kanye_raw)

# Place Kanye’s image near bottom of canvas
kanye_item = canvas.create_image(
    bg_width // 2,   # x = center
    bg_height - 70,  # y = 70px up from bottom
    image=kanye_img
)

# Bind a click event to Kanye’s image
canvas.tag_bind(kanye_item, "<Button-1>", flip_kanye)
canvas.tag_bind(kanye_item, "<Button-1>", get_quote, add="+")


# Start main loop
window.mainloop()
