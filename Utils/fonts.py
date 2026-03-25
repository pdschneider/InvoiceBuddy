# Utils/fonts.py
from config import globals

# Fonts
if globals.os_name.startswith("Windows"):
    title_font   = ("DejaVu Sans", 18, "bold")
    heading_font = ("DejaVu Sans", 16, "bold")
    body_font    = ("DejaVu Sans", 14)
    mono_font    = ("DejaVu Sans Mono", 10)
    button_font  = ("DejaVu Sans", 30)
elif globals.os_name.startswith("Linux"):
    title_font   = ("Ubuntu", 18, "bold")
    heading_font = ("Ubuntu", 16, "bold")
    body_font    = ("Ubuntu", 14)
    mono_font    = ("Ubuntu Mono", 10)
    button_font  = ("Ubuntu", 30)
else:  # macOS or anything else
    title_font   = ("Helvetica Neue", 18, "bold")
    heading_font = ("Helvetica Neue", 16, "bold")
    body_font    = ("Helvetica Neue", 14)
    mono_font    = ("SF Mono", 11)
    button_font  = ("Helvetica Neue", 30)
