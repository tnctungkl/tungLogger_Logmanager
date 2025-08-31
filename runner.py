from __future__ import annotations
import tkinter as tk
from gui import LogManagerApp

def main():
    root = tk.Tk()
    app = LogManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()