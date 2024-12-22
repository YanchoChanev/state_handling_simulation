# main.py
# Application Entry Point

import tkinter as tk
from ui import TCPClientApp

if __name__ == "__main__":
    root = tk.Tk()
    app = TCPClientApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
