import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
import config
from theme import setup_theme, VLC_ORANGE


class MainApp:
    def __init__(self, root: tb.Window):
        self.root = root
        self.root.title("YT → VLC Launcher")
        self.root.geometry("820x620")
        self.root.minsize(700, 500)

        # Load configuration
        self.cfg = config.load_config()

        # Setup custom theme
        self.style = setup_theme(self.root.style)

        # Keyboard shortcuts
        self.root.bind("<Control-d>", self._toggle_debug_shortcut)
        self.root.bind("<Control-D>", self._toggle_debug_shortcut)

        # Main notebook (Tab control)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Play / Download
        from gui.play_tab import PlayTab
        self.play_tab = PlayTab(self.notebook, self)
        self.notebook.add(self.play_tab, text="  ▶ Play / Download  ")

        # Tab 2: Watch History
        from gui.history_tab import HistoryTab
        self.history_tab = HistoryTab(self.notebook, self)
        self.notebook.add(self.history_tab, text="  🕒 Watch History  ")

        # Tab 3: Pinned Favourites
        from gui.favourites_tab import FavouritesTab
        self.favourites_tab = FavouritesTab(self.notebook, self)
        self.notebook.add(self.favourites_tab, text="  ⭐ Favourites  ")

        # Tab 4: Persistent Playlists
        from gui.playlists_tab import PlaylistsTab
        self.playlists_tab = PlaylistsTab(self.notebook, self)
        self.notebook.add(self.playlists_tab, text="  📁 Playlists  ")

        # Tab 5: Settings & Backup
        from gui.settings_tab import SettingsTab
        self.settings_tab = SettingsTab(self.notebook, self)
        self.notebook.add(self.settings_tab, text="  ⚙️ Settings  ")

        # Status Bar at bottom
        self.status_bar = ttk.Frame(self.root, padding=(8, 4))
        self.status_bar.pack(fill="x", side="bottom")

        self.status_label = ttk.Label(
            self.status_bar,
            text="Ready",
            style="Muted.TLabel"
        )
        self.status_label.pack(side="left")

        self.debug_status = ttk.Label(
            self.status_bar,
            text="DEBUG: ON" if config.get("debug_mode", False) else "DEBUG: OFF",
            style="Muted.TLabel"
        )
        self.debug_status.pack(side="right")

    def _toggle_debug_shortcut(self, event=None):
        current = config.get("debug_mode", False)
        new_val = not current
        config.set_value("debug_mode", new_val)
        self.debug_status.config(
            text="DEBUG: ON" if new_val else "DEBUG: OFF",
            foreground=VLC_ORANGE if new_val else "#aaaaaa"
        )
        self.set_status(f"Debug mode {'enabled' if new_val else 'disabled'}")
        return "break"

    def set_status(self, text: str):
        self.status_label.config(text=text)
