import os
import sys
import threading
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as tb

import config
import vlc_utils
import ytdlp_utils
import export_import
from theme import VLC_ORANGE, VLC_PANEL_BG, VLC_TEXT, VLC_TEXT_MUTED


class SettingsTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=14)
        self.app = app
        self.root = app.root

        self._build_ui()
        self.load_current_values()

    def _build_ui(self):
        # Canvas/Scrollable container for clean responsiveness
        container = tb.Frame(self)
        container.pack(fill="both", expand=True)

        # --- Section 1: Playback & VLC ---
        vlc_group = tb.LabelFrame(container, text=" 🎬 Playback & Media Player ", padding=12)
        vlc_group.pack(fill="x", pady=(0, 10))

        vlc_row = tb.Frame(vlc_group)
        vlc_row.pack(fill="x", pady=2)
        tb.Label(vlc_row, text="VLC Path:", width=16, font=("Segoe UI", 9, "bold")).pack(side="left")
        self.vlc_path_var = tk.StringVar()
        self.vlc_entry = tb.Entry(vlc_row, textvariable=self.vlc_path_var, font=("Segoe UI", 9))
        self.vlc_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tb.Button(vlc_row, text="Browse...", style="Action.TButton", command=self._browse_vlc).pack(side="right")

        opts_row = tb.Frame(vlc_group)
        opts_row.pack(fill="x", pady=(8, 0))

        tb.Label(opts_row, text="Default Mode:", width=16).pack(side="left")
        self.default_mode_var = tk.StringVar(value="stream")
        tb.Radiobutton(opts_row, text="Stream Now", variable=self.default_mode_var, value="stream", bootstyle="warning", command=self._save_setting).pack(side="left", padx=(0, 12))
        tb.Radiobutton(opts_row, text="Download Media", variable=self.default_mode_var, value="download", bootstyle="warning", command=self._save_setting).pack(side="left")

        # --- Section 2: Smart Downloads & Quality ---
        dl_group = tb.LabelFrame(container, text=" 📥 Smart Downloads & Storage ", padding=12)
        dl_group.pack(fill="x", pady=(0, 10))

        dir_row = tb.Frame(dl_group)
        dir_row.pack(fill="x", pady=2)
        tb.Label(dir_row, text="Download Folder:", width=16, font=("Segoe UI", 9, "bold")).pack(side="left")
        self.dl_dir_var = tk.StringVar()
        self.dl_dir_entry = tb.Entry(dir_row, textvariable=self.dl_dir_var, font=("Segoe UI", 9))
        self.dl_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tb.Button(dir_row, text="Change...", style="Action.TButton", command=self._browse_dl_dir).pack(side="right")

        q_row = tb.Frame(dl_group)
        q_row.pack(fill="x", pady=(8, 4))
        tb.Label(q_row, text="Default Quality:", width=16).pack(side="left")
        self.default_quality_var = tk.StringVar(value="720p")
        quality_choices = list(ytdlp_utils.FORMAT_MAP.keys())
        self.q_combo = tb.Combobox(q_row, textvariable=self.default_quality_var, values=quality_choices, state="readonly", width=18, bootstyle="warning")
        self.q_combo.pack(side="left", padx=(0, 12))
        self.q_combo.bind("<<ComboboxSelected>>", lambda e: self._save_setting())

        tb.Label(q_row, text="Size Warning (MB):").pack(side="left", padx=(10, 4))
        self.warn_size_var = tk.StringVar(value="1024")
        self.warn_size_entry = tb.Entry(q_row, textvariable=self.warn_size_var, width=8)
        self.warn_size_entry.pack(side="left")
        self.warn_size_entry.bind("<FocusOut>", lambda e: self._save_setting())

        toggles_row = tb.Frame(dl_group)
        toggles_row.pack(fill="x", pady=(6, 0))

        self.auto_open_var = tk.BooleanVar(value=True)
        tb.Checkbutton(toggles_row, text="Auto-open in VLC after download completes", variable=self.auto_open_var, bootstyle="warning-round-toggle", command=self._save_setting).pack(side="left", padx=(0, 16))

        self.paste_go_var = tk.BooleanVar(value=False)
        tb.Checkbutton(toggles_row, text="Paste-and-Go (Auto-play when pasting a URL)", variable=self.paste_go_var, bootstyle="warning-round-toggle", command=self._save_setting).pack(side="left")

        # --- Section 3: Watch History & Backup (NewPipe Style) ---
        hist_group = tb.LabelFrame(container, text=" 🕒 Watch History & Backup / Restore ", padding=12)
        hist_group.pack(fill="x", pady=(0, 10))

        h_row = tb.Frame(hist_group)
        h_row.pack(fill="x", pady=2)
        tb.Label(h_row, text="History Limit:", width=16).pack(side="left")
        self.history_cap_var = tk.StringVar(value="500")
        self.cap_entry = tb.Entry(h_row, textvariable=self.history_cap_var, width=8)
        self.cap_entry.pack(side="left", padx=(0, 16))
        self.cap_entry.bind("<FocusOut>", lambda e: self._save_setting())

        self.auto_clean_var = tk.BooleanVar(value=False)
        tb.Checkbutton(h_row, text="Auto-clean stream history older than 30 days", variable=self.auto_clean_var, bootstyle="warning-round-toggle", command=self._save_setting).pack(side="left")

        # Backup & Restore Row (NewPipe style)
        backup_row = tb.Frame(hist_group)
        backup_row.pack(fill="x", pady=(10, 0))

        tb.Label(backup_row, text="Data Portability:", width=16, font=("Segoe UI", 9, "bold")).pack(side="left")

        tb.Button(
            backup_row,
            text="📦 Export Backup ZIP",
            style="VLC.TButton",
            command=self._export_backup
        ).pack(side="left", padx=(0, 8))

        tb.Button(
            backup_row,
            text="📥 Import Backup ZIP",
            style="Action.TButton",
            command=self._import_backup
        ).pack(side="left")

        # --- Section 4: Diagnostics & System ---
        sys_group = tb.LabelFrame(container, text=" 🛠️ Diagnostics & Updates ", padding=12)
        sys_group.pack(fill="x")

        sys_row = tb.Frame(sys_group)
        sys_row.pack(fill="x", pady=2)

        self.debug_var = tk.BooleanVar(value=config.get("debug_mode", False))
        tb.Checkbutton(
            sys_row,
            text="Debug Mode (verbose logs, Ctrl+D shortcut)",
            variable=self.debug_var,
            bootstyle="warning-round-toggle",
            command=self._toggle_debug
        ).pack(side="left", padx=(0, 16))

        self.update_btn = tb.Button(
            sys_row,
            text="🔄 Check for yt-dlp Updates",
            style="Action.TButton",
            command=self._check_ytdlp_update
        )
        self.update_btn.pack(side="right")

        self.env_label = tb.Label(
            sys_group,
            text=f"Python {sys.version.split()[0]}  |  Node.js: {'Detected' if shutil.which('node') else 'Not Found'}",
            style="Muted.TLabel"
        )
        self.env_label.pack(anchor="w", pady=(6, 0))

    def load_current_values(self):
        cfg = config.load_config()
        vlc_val = cfg.get("vlc_path", "")
        self.vlc_path_var.set(vlc_val)
        if not vlc_val:
            vlc_utils.find_vlc_path_async(
                lambda p: self.root.after(0, lambda: self.vlc_path_var.set(p or "")) if p else None
            )
        self.dl_dir_var.set(cfg.get("download_dir", ""))
        self.default_mode_var.set(cfg.get("default_mode", "stream"))
        self.default_quality_var.set(cfg.get("default_quality", "720p"))
        self.warn_size_var.set(str(cfg.get("warn_size_threshold_mb", 1024)))
        self.auto_open_var.set(cfg.get("auto_open_vlc", True))
        self.paste_go_var.set(cfg.get("paste_and_go", False))
        self.history_cap_var.set(str(cfg.get("history_cap", 500)))
        self.auto_clean_var.set(cfg.get("auto_clean_history", False))
        self.debug_var.set(cfg.get("debug_mode", False))

    def _save_setting(self):
        try:
            warn_mb = int(self.warn_size_var.get().strip() or "1024")
        except ValueError:
            warn_mb = 1024

        try:
            cap = int(self.history_cap_var.get().strip() or "500")
        except ValueError:
            cap = 500

        config.set_value("vlc_path", self.vlc_path_var.get().strip())
        config.set_value("download_dir", self.dl_dir_var.get().strip())
        config.set_value("default_mode", self.default_mode_var.get())
        config.set_value("default_quality", self.default_quality_var.get())
        config.set_value("warn_size_threshold_mb", warn_mb)
        config.set_value("auto_open_vlc", self.auto_open_var.get())
        config.set_value("paste_and_go", self.paste_go_var.get())
        config.set_value("history_cap", cap)
        config.set_value("auto_clean_history", self.auto_clean_var.get())
        config.set_value("debug_mode", self.debug_var.get())

        self.app.set_status("Settings saved")

    def _browse_vlc(self):
        fn = filedialog.askopenfilename(title="Select VLC Player Executable", filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")])
        if fn:
            self.vlc_path_var.set(fn)
            self._save_setting()

    def _browse_dl_dir(self):
        folder = filedialog.askdirectory(title="Select Download Directory", initialdir=self.dl_dir_var.get())
        if folder:
            self.dl_dir_var.set(folder)
            self._save_setting()
            if hasattr(self.app, "play_tab"):
                self.app.play_tab.download_dir = folder
                self.app.play_tab.dl_path_label.config(text=folder)

    def _toggle_debug(self):
        self._save_setting()
        new_val = self.debug_var.get()
        self.app.debug_status.config(
            text="DEBUG: ON" if new_val else "DEBUG: OFF",
            foreground=VLC_ORANGE if new_val else "#aaaaaa"
        )
        self.app.set_status(f"Debug mode {'enabled' if new_val else 'disabled'}")

    def _export_backup(self):
        dest = filedialog.asksaveasfilename(
            title="Export YT-VLC Backup",
            defaultextension=".zip",
            filetypes=[("ZIP Backup Archive", "*.zip")],
            initialfile="yt_vlc_backup.zip"
        )
        if dest:
            ok, msg = export_import.export_backup(dest)
            if ok:
                messagebox.showinfo("Backup Exported", f"{msg}\n\nSaved to:\n{dest}")
                self.app.set_status("Backup exported successfully")
            else:
                messagebox.showerror("Export Failed", msg)

    def _import_backup(self):
        src = filedialog.askopenfilename(
            title="Restore YT-VLC Backup",
            filetypes=[("ZIP Backup Archive", "*.zip"), ("All Files", "*.*")]
        )
        if src:
            if not messagebox.askyesno("Restore Backup", "Restoring from backup will merge and update your history, playlists, and favourites.\n\nDo you want to proceed?"):
                return
            ok, msg, stats = export_import.import_backup(src)
            if ok:
                messagebox.showinfo("Backup Restored", f"{msg}\n\nAll tabs will now be refreshed.")
                # Refresh all tabs
                if hasattr(self.app, "history_tab"):
                    self.app.history_tab.refresh()
                if hasattr(self.app, "favourites_tab"):
                    self.app.favourites_tab.refresh()
                if hasattr(self.app, "playlists_tab"):
                    self.app.playlists_tab.refresh()
                self.load_current_values()
                self.app.set_status("Backup restored")
            else:
                messagebox.showerror("Restore Failed", msg)

    def _check_ytdlp_update(self):
        self.update_btn.config(state="disabled", text="⏳ Checking...")
        self.app.set_busy(True, "Checking for yt-dlp update on PyPI...")

        def check():
            info = ytdlp_utils.get_version_info()
            self.root.after(0, lambda: self._on_version_result(info))

        threading.Thread(target=check, daemon=True).start()

    def _on_version_result(self, info):
        self.update_btn.config(state="normal", text="🔄 Check for yt-dlp Updates")
        self.app.set_busy(False)
        installed = info.get("installed")
        latest = info.get("latest")
        if info.get("update_available"):
            if messagebox.askyesno("Update Available", f"A newer version of yt-dlp is available!\n\nInstalled: {installed}\nLatest: {latest}\n\nWould you like to update now?"):
                self._run_ytdlp_update()
        elif latest:
            messagebox.showinfo("Up to Date", f"yt-dlp is up to date!\n\nInstalled version: {installed}")
            self.app.set_status("yt-dlp is up to date")
        else:
            messagebox.showinfo("Version Check", f"Installed version: {installed}\n(Could not reach PyPI to check latest version)")

    def _run_ytdlp_update(self):
        self.app.set_busy(True, "Updating yt-dlp in background...")
        if hasattr(self.app, "play_tab"):
            self.app.play_tab.log("Starting yt-dlp update via pip...")

        def update():
            success = ytdlp_utils.update_ytdlp(
                log_callback=lambda m: self.app.play_tab.log(m) if hasattr(self.app, "play_tab") else None
            )
            self.root.after(0, lambda: self.app.set_busy(False, "yt-dlp update finished"))
            self.root.after(0, lambda: messagebox.showinfo("Update Complete", "yt-dlp has been updated! Please restart the app.") if success else messagebox.showerror("Update Failed", "yt-dlp update encountered an error. Check Activity Log."))

        threading.Thread(target=update, daemon=True).start()
