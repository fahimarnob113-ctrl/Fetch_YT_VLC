import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as tb

import config
import vlc_utils
import ytdlp_utils
import history
from theme import VLC_ORANGE, VLC_DARK_BG, VLC_PANEL_BG, VLC_INPUT_BG, VLC_TEXT


class PlayTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self.root = app.root

        self.vlc_path = vlc_utils.find_vlc_path() or config.get("vlc_path", "")
        self.download_dir = config.get("download_dir", os.path.join(os.path.expanduser("~"), "Videos", "YT-VLC-Downloads"))
        self.is_working = False
        self._cancel_flag = False

        self._build_ui()

    def _build_ui(self):
        # 1. Dependency Warning Banner (if yt-dlp missing)
        if not ytdlp_utils.is_ytdlp_available():
            self.warn_banner = tb.Frame(self, bootstyle="danger", padding=8)
            self.warn_banner.pack(fill="x", pady=(0, 10))
            tb.Label(
                self.warn_banner,
                text="⚠️ yt-dlp is not installed! Run: pip install yt-dlp",
                bootstyle="inverse-danger",
                font=("Segoe UI", 10, "bold")
            ).pack(side="left")

        # 2. URL Input Section
        url_frame = tb.LabelFrame(self, text=" YouTube URL ", padding=10)
        url_frame.pack(fill="x", pady=(0, 10))

        entry_row = tb.Frame(url_frame)
        entry_row.pack(fill="x")

        self.url_var = tk.StringVar()
        self.url_entry = tb.Entry(
            entry_row,
            textvariable=self.url_var,
            font=("Segoe UI", 10)
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.url_entry.bind("<Return>", lambda e: self.on_go())

        tb.Button(
            entry_row,
            text="Paste",
            style="Action.TButton",
            command=self._paste_from_clipboard
        ).pack(side="left", padx=(0, 4))

        tb.Button(
            entry_row,
            text="Clear",
            style="Action.TButton",
            command=lambda: self.url_var.set("")
        ).pack(side="left")

        # Validation feedback label
        self.validation_label = tb.Label(url_frame, text="", style="Muted.TLabel")
        self.validation_label.pack(anchor="w", pady=(4, 0))

        # 3. Mode & Quality Section
        opts_frame = tb.Frame(self)
        opts_frame.pack(fill="x", pady=(0, 8))

        # Mode Selection
        mode_group = tb.LabelFrame(opts_frame, text=" Playback Mode ", padding=10)
        mode_group.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.mode_var = tk.StringVar(value=config.get("default_mode", "stream"))
        self.radio_stream = tb.Radiobutton(
            mode_group,
            text="Stream Now (Direct to VLC, no files saved)",
            variable=self.mode_var,
            value="stream",
            bootstyle="warning",
            command=self._on_mode_change
        )
        self.radio_stream.pack(anchor="w", pady=2)

        self.radio_download = tb.Radiobutton(
            mode_group,
            text="Download for Offline Viewing (Save to disk)",
            variable=self.mode_var,
            value="download",
            bootstyle="warning",
            command=self._on_mode_change
        )
        self.radio_download.pack(anchor="w", pady=2)

        # Quality Selection
        quality_group = tb.LabelFrame(opts_frame, text=" Quality / Format ", padding=10)
        quality_group.pack(side="left", fill="both", expand=True, padx=(6, 0))

        quality_choices = list(ytdlp_utils.FORMAT_MAP.keys())
        default_q = config.get("default_quality", "720p")
        if default_q not in quality_choices:
            default_q = "720p"

        self.quality_var = tk.StringVar(value=default_q)
        self.quality_combo = tb.Combobox(
            quality_group,
            textvariable=self.quality_var,
            values=quality_choices,
            state="readonly",
            bootstyle="warning"
        )
        self.quality_combo.pack(fill="x", pady=(4, 2))

        tb.Label(
            quality_group,
            text="Default 720p saves bandwidth & disk space",
            style="Muted.TLabel"
        ).pack(anchor="w")

        # 4. Download Directory Row (Interactive)
        self.dl_frame = tb.LabelFrame(self, text=" Download Folder ", padding=(10, 6))
        self.dl_frame.pack(fill="x", pady=(0, 8))

        self.dl_path_label = tb.Label(
            self.dl_frame,
            text=self.download_dir,
            font=("Segoe UI", 9)
        )
        self.dl_path_label.pack(side="left", fill="x", expand=True)

        tb.Button(
            self.dl_frame,
            text="📁 Open Folder",
            style="Action.TButton",
            command=self._open_download_folder
        ).pack(side="right", padx=(4, 0))

        tb.Button(
            self.dl_frame,
            text="Change...",
            style="Action.TButton",
            command=self._choose_download_dir
        ).pack(side="right")

        # 5. VLC Executable Row
        vlc_box = tb.Frame(self)
        vlc_box.pack(fill="x", pady=(0, 8))

        tb.Label(vlc_box, text="VLC Player:", font=("Segoe UI", 9, "bold")).pack(side="left")

        self.vlc_status_label = tb.Label(
            vlc_box,
            text=self.vlc_path if self.vlc_path else "Not found - Click Browse",
            bootstyle="success" if self.vlc_path else "danger",
            font=("Segoe UI", 9)
        )
        self.vlc_status_label.pack(side="left", padx=10, fill="x", expand=True)

        tb.Button(
            vlc_box,
            text="Browse...",
            style="Action.TButton",
            command=self._browse_vlc
        ).pack(side="right")

        # 6. Action Row: Go Button & Cancel Button
        action_box = tb.Frame(self)
        action_box.pack(fill="x", pady=(0, 6))

        self.go_btn = tb.Button(
            action_box,
            text="▶  Play in VLC",
            bootstyle="warning",
            style="VLC.TButton",
            command=self.on_go
        )
        self.go_btn.pack(side="left", fill="x", expand=True, ipady=4)

        self.cancel_btn = tb.Button(
            action_box,
            text="✖ Cancel",
            bootstyle="danger-outline",
            command=self._cancel_task,
            state="disabled"
        )
        self.cancel_btn.pack(side="right", padx=(8, 0))

        # 7. Visual Progress Bar for Downloads
        self.progress_frame = tb.Frame(self)
        self.progress_frame.pack(fill="x", pady=(0, 6))

        self.progress_bar = tb.Progressbar(
            self.progress_frame,
            bootstyle="warning-striped",
            mode="determinate"
        )
        self.progress_bar.pack(fill="x", side="top", pady=(0, 2))

        self.progress_label = tb.Label(
            self.progress_frame,
            text="",
            style="Muted.TLabel"
        )
        self.progress_label.pack(side="left")

        # 8. Activity Log Area
        log_header = tb.Frame(self)
        log_header.pack(fill="x", pady=(2, 2))
        tb.Label(log_header, text="Activity Log", font=("Segoe UI", 9, "bold")).pack(side="left")

        tb.Button(
            log_header,
            text="Clear Log",
            style="Action.TButton",
            command=self._clear_log
        ).pack(side="right")

        self.log_text = tk.Text(
            self,
            height=7,
            bg=VLC_INPUT_BG,
            fg=VLC_TEXT,
            insertbackground=VLC_ORANGE,
            relief="flat",
            font=("Consolas", 9),
            wrap="word",
            state="disabled"
        )
        self.log_text.pack(fill="both", expand=True)

        # Initial Welcome in Log
        self.log("YT → VLC Launcher ready.")
        if self.vlc_path:
            self.log(f"VLC found: {self.vlc_path}")
        else:
            self.log("⚠️ VLC not detected automatically. Please click 'Browse...' to select vlc.exe.")

        self._on_mode_change()

    def _paste_from_clipboard(self):
        try:
            text = self.root.clipboard_get()
            if text:
                self.url_var.set(text.strip())
                self.validation_label.config(text="")
                if config.get("paste_and_go", False):
                    self.on_go()
        except Exception:
            pass

    def _on_mode_change(self):
        mode = self.mode_var.get()
        if mode == "stream":
            self.go_btn.config(text="▶  Play in VLC", bootstyle="warning")
            self.dl_path_label.config(bootstyle="secondary")
        else:
            self.go_btn.config(text="📥  Download Media", bootstyle="warning")
            self.dl_path_label.config(bootstyle="info")

    def _choose_download_dir(self):
        folder = filedialog.askdirectory(
            title="Select Download Directory",
            initialdir=self.download_dir
        )
        if folder:
            self.download_dir = folder
            config.set_value("download_dir", folder)
            self.dl_path_label.config(text=folder)
            self.log(f"Download directory set to: {folder}")

    def _open_download_folder(self):
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir, exist_ok=True)
        try:
            if sys.platform.startswith("win"):
                os.startfile(self.download_dir)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", self.download_dir])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", self.download_dir])
        except Exception as e:
            self.log(f"Could not open directory: {e}")

    def _browse_vlc(self):
        filename = filedialog.askopenfilename(
            title="Locate VLC Executable",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )
        if filename and os.path.isfile(filename):
            self.vlc_path = filename
            config.set_value("vlc_path", filename)
            self.vlc_status_label.config(text=filename, bootstyle="success")
            self.log(f"VLC path updated: {filename}")

    def _cancel_task(self):
        if self.is_working:
            self._cancel_flag = True
            self.log("⚠️ Cancellation requested...")
            self.cancel_btn.config(state="disabled")

    def log(self, message: str):
        """Thread-safe logging to the text box."""
        def append():
            self.log_text.config(state="normal")
            self.log_text.insert("end", f"{message}\n")
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.root.after(0, append)

    def _clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def on_go(self):
        if self.is_working:
            return

        raw_url = self.url_var.get().strip()
        is_valid, err_msg = ytdlp_utils.validate_url(raw_url)
        if not is_valid:
            self.validation_label.config(text=f"❌ {err_msg}", foreground="#e74c3c")
            messagebox.showwarning("Invalid URL", err_msg)
            return
        self.validation_label.config(text="")

        if not self.vlc_path or not os.path.isfile(self.vlc_path):
            messagebox.showerror(
                "VLC Required",
                "VLC executable not found! Please click 'Browse...' to select your VLC player."
            )
            return

        mode = self.mode_var.get()
        quality = self.quality_var.get()

        # Update UI to working state
        self.is_working = True
        self._cancel_flag = False
        self.cancel_btn.config(state="normal")
        self.progress_bar["value"] = 0
        self.progress_label.config(text="Preparing...")

        action_text = "⏳ Resolving Media..." if mode == "stream" else "⏳ Downloading..."
        self.go_btn.config(state="disabled", text=action_text)
        self.app.set_status(f"Working ({mode})...")

        # Spawn worker thread
        threading.Thread(
            target=self._worker,
            args=(raw_url, mode, quality),
            daemon=True
        ).start()

    def _worker(self, url: str, mode: str, quality: str):
        try:
            if mode == "stream":
                self.log(f"Resolving stream URLs for {url} ({quality})...")
                entries, meta = ytdlp_utils.resolve_urls(url, quality=quality, log_callback=self.log)

                self.log(f"Handing {len(entries)} item(s) to VLC...")
                vlc_utils.launch_vlc(self.vlc_path, entries, log_callback=self.log)

                # Record in history
                for item in entries:
                    history.add_entry(
                        title=item["title"],
                        source_url=url,
                        kind="streamed",
                        duration=item.get("duration", "")
                    )

                self.log("✅ Playback started in VLC.")
                self.root.after(0, lambda: self.app.set_status("VLC playback active"))

            else:  # Download Mode
                self.log(f"Estimating download size for: {url} ({quality})...")
                est_bytes, is_approx = ytdlp_utils.estimate_size(url, quality=quality, log_callback=self.log)

                if est_bytes > 0:
                    est_mb = est_bytes / (1024 * 1024)
                    approx_tag = "approx. " if is_approx else ""
                    self.log(f"Estimated size: {approx_tag}{est_mb:.1f} MB")

                    # Smart size threshold check
                    warn_mb = config.get("warn_size_threshold_mb", 1024)
                    if est_mb > warn_mb:
                        proceed = messagebox.askyesno(
                            "Large Download Warning",
                            f"The estimated download size is {approx_tag}{est_mb:.1f} MB (exceeds {warn_mb} MB limit).\n\n"
                            f"Do you want to proceed with downloading at {quality}?"
                        )
                        if not proceed:
                            self.log("Download cancelled by user (size warning).")
                            return

                def progress_hook(d):
                    if self._cancel_flag:
                        raise RuntimeError("Download cancelled by user.")
                    if d.get("status") == "downloading":
                        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                        downloaded = d.get("downloaded_bytes") or 0
                        pct = (downloaded / total * 100) if total > 0 else 0
                        pct_str = d.get("_percent_str", f"{pct:.1f}%").strip()
                        speed = d.get("_speed_str", "").strip()
                        eta = d.get("_eta_str", "").strip()
                        fname = os.path.basename(d.get("filename", ""))

                        status_txt = f"{pct_str} | {speed} | ETA: {eta}" if speed else f"{pct_str}"
                        self.root.after(0, lambda: self._update_progress(pct, status_txt))

                downloaded_files = ytdlp_utils.download_locally(
                    input_url=url,
                    download_dir=self.download_dir,
                    quality=quality,
                    progress_hook=progress_hook,
                    log_callback=self.log,
                    cancel_check=lambda: self._cancel_flag
                )

                if not downloaded_files:
                    raise RuntimeError("No files were successfully downloaded.")

                self.root.after(0, lambda: self._update_progress(100, "Download Complete!"))
                self.log(f"✅ Successfully downloaded {len(downloaded_files)} file(s).")

                # Record each file in history
                for title, fpath in downloaded_files:
                    history.add_entry(
                        title=title,
                        source_url=url,
                        kind="downloaded",
                        file_path=fpath
                    )

                # Auto-open in VLC if enabled in config
                if config.get("auto_open_vlc", True):
                    self.log("Opening downloaded file(s) in VLC...")
                    vlc_utils.launch_vlc(self.vlc_path, downloaded_files, log_callback=self.log)

                self.root.after(0, lambda: self.app.set_status("Download complete"))

        except Exception as e:
            self.log(f"❌ ERROR: {e}")
            if config.get("debug_mode", False):
                import traceback
                self.log(traceback.format_exc())
            self.root.after(0, lambda: messagebox.showerror("Operation Error", str(e)))
            self.root.after(0, lambda: self.app.set_status("Error occurred"))
        finally:
            self.root.after(0, self._reset_work_state)

    def _update_progress(self, percent: float, label_text: str):
        self.progress_bar["value"] = percent
        self.progress_label.config(text=label_text)

    def _reset_work_state(self):
        self.is_working = False
        self._cancel_flag = False
        self.cancel_btn.config(state="disabled")
        mode = self.mode_var.get()
        btn_text = "▶  Play in VLC" if mode == "stream" else "📥  Download Media"
        self.go_btn.config(state="normal", text=btn_text)
        self.app.set_status("Ready")
        if hasattr(self.app, "history_tab") and hasattr(self.app.history_tab, "refresh"):
            self.app.history_tab.refresh()
