"""
Helper functions for UI management.
"""

def center_window(window, width: int, height: int):
    """
    Centers a Tkinter window on the screen.
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))

    window.geometry(f"{width}x{height}+{x}+{y}")

def clear_frame(frame):
    """
    Destroys all child widgets inside a given tkinter frame.
    """
    for child in frame.winfo_children():
        child.destroy()
