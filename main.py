#!/usr/bin/env python3
"""
YT -> VLC Launcher
Main Application Entry Point
"""

import sys
import os

# Ensure current directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ttkbootstrap as tb
from gui.app import MainApp


def main():
    root = tb.Window(themename="darkly")

    # Set application icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "the logo or icon", "app_icon.ico")
    if os.path.isfile(icon_path):
        try:
            root.iconbitmap(icon_path)
        except Exception:
            pass

    app = MainApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
