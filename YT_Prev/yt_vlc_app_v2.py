#!/usr/bin/env python3
"""
YT-VLC Launcher (v2)
---------------------
A standalone GUI app that:
  - Streams a YouTube video/playlist straight into VLC, OR
  - Downloads it locally for offline playback
  - Keeps a watch history log (what you played/downloaded and when),
    with one-click replay from history

Requirements:
    - Python 3.8+
    - yt-dlp installed (pip install yt-dlp)
    - VLC installed on your system

Usage:
    python yt_vlc_app.py
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    import yt_dlp
except ImportError:
    yt_dlp = None


HISTORY_PATH = os.path.join(os.path.expanduser("~"), ".yt_vlc_history.json")
DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Videos", "YT-VLC-Downloads")


# ---------------------------------------------------------------------------
# VLC discovery
# ---------------------------------------------------------------------------

def find_vlc_path():
    for name in ("vlc", "vlc.exe"):
        path = shutil.which(name)
        if path:
            return path

    candidates = []
    if sys.platform.startswith("win"):
        candidates = [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        ]
    elif sys.platform == "darwin":
        candidates = ["/Applications/VLC.app/Contents/MacOS/VLC"]
    else:
        candidates = ["/usr/bin/vlc", "/usr/local/bin/vlc", "/snap/bin/vlc"]

    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


# ---------------------------------------------------------------------------
# Watch history persistence
# ---------------------------------------------------------------------------

def load_history():
    if not os.path.isfile(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_history(entries):
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
    except OSError:
        pass


def add_history_entry(title, source_url, kind, file_path=None):
    """kind: 'streamed' or 'downloaded'"""
    entries = load_history()
    entries.insert(0, {
        "title": title,
        "source_url": source_url,
        "kind": kind,
        "file_path": file_path,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    })
    # Keep history to a reasonable size
    entries = entries[:500]
    save_history(entries)


# ---------------------------------------------------------------------------
# yt-dlp: resolve stream URLs (for streaming mode)
# ---------------------------------------------------------------------------

def resolve_urls(input_url, log_callback):
    if yt_dlp is None:
        raise RuntimeError("yt-dlp is not installed. Run: pip install yt-dlp")

    ydl_opts = {"quiet": True, "no_warnings": True, "format": "best", "noplaylist": False}
    log_callback(f"Resolving: {input_url}")
    results = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(input_url, download=False)
        if "entries" in info:
            entries = [e for e in info["entries"] if e]
            log_callback(f"Found playlist with {len(entries)} videos")
            for entry in entries:
                stream_url = entry.get("url")
                title = entry.get("title", "Unknown")
                if stream_url:
                    results.append((title, stream_url))
                else:
                    log_callback(f"  Skipping (no stream found): {title}")
        else:
            title = info.get("title", "Unknown")
            stream_url = info.get("url")
            if stream_url:
                results.append((title, stream_url))

    return results


# ---------------------------------------------------------------------------
# yt-dlp: download locally (for offline mode)
# ---------------------------------------------------------------------------

def download_locally(input_url, download_dir, log_callback):
    """
    Downloads the video/playlist to disk. Returns a list of
    (title, local_file_path) tuples for everything successfully downloaded.
    """
    if yt_dlp is None:
        raise RuntimeError("yt-dlp is not installed. Run: pip install yt-dlp")

    os.makedirs(download_dir, exist_ok=True)
    downloaded = []

    def progress_hook(d):
        if d.get("status") == "downloading":
            pct = d.get("_percent_str", "").strip()
            fname = os.path.basename(d.get("filename", ""))
            log_callback(f"  Downloading {fname}: {pct}")
        elif d.get("status") == "finished":
            log_callback(f"  Finished: {os.path.basename(d.get('filename', ''))}")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "best",
        "outtmpl": os.path.join(download_dir, "%(playlist_title|)s%(playlist_index& - |)s%(title)s.%(ext)s"),
        "progress_hooks": [progress_hook],
        "noplaylist": False,
    }

    log_callback(f"Downloading to: {download_dir}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(input_url, download=True)
        entries = info["entries"] if "entries" in info else [info]
        for entry in entries:
            if not entry:
                continue
            title = entry.get("title", "Unknown")
            # Reconstruct the actual output path yt-dlp used
            try:
                filepath = ydl.prepare_filename(entry)
            except Exception:
                filepath = None
            if filepath and os.path.isfile(filepath):
                downloaded.append((title, filepath))
            else:
                log_callback(f"  Warning: couldn't confirm file for '{title}'")

    return downloaded


# ---------------------------------------------------------------------------
# VLC launch
# ---------------------------------------------------------------------------

def launch_vlc(vlc_path, items, log_callback):
    """items: list of (title, url_or_path). Single item plays directly;
    multiple builds a temporary .m3u playlist."""
    if not items:
        raise RuntimeError("Nothing to play.")

    if len(items) == 1:
        _, target = items[0]
        log_callback("Launching VLC...")
        subprocess.Popen([vlc_path, target])
        return

    fd, m3u_path = tempfile.mkstemp(suffix=".m3u", prefix="yt_vlc_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for title, target in items:
            f.write(f"#EXTINF:-1,{title}\n{target}\n")

    log_callback(f"Launching VLC with {len(items)} items...")
    subprocess.Popen([vlc_path, m3u_path])


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class YtVlcApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YT → VLC Launcher")
        self.root.geometry("640x520")
        self.vlc_path = find_vlc_path()
        self.download_dir = DEFAULT_DOWNLOAD_DIR

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        self.play_tab = tk.Frame(notebook)
        self.history_tab = tk.Frame(notebook)
        notebook.add(self.play_tab, text="Play / Download")
        notebook.add(self.history_tab, text="History")

        self._build_play_tab()
        self._build_history_tab()
        self._refresh_history()

    # -------------------- Play / Download tab --------------------

    def _build_play_tab(self):
        pad = {"padx": 12, "pady": 6}
        f = self.play_tab

        tk.Label(f, text="YouTube video or playlist URL:").pack(anchor="w", **pad)
        self.url_entry = tk.Entry(f, width=70)
        self.url_entry.pack(fill="x", **pad)

        # Mode selector
        mode_frame = tk.Frame(f)
        mode_frame.pack(fill="x", **pad)
        self.mode_var = tk.StringVar(value="stream")
        tk.Radiobutton(mode_frame, text="Stream now (play in VLC, don't save)",
                        variable=self.mode_var, value="stream",
                        command=self._toggle_mode).pack(anchor="w")
        tk.Radiobutton(mode_frame, text="Download for offline viewing",
                        variable=self.mode_var, value="download",
                        command=self._toggle_mode).pack(anchor="w")

        # Download folder row
        self.dl_frame = tk.Frame(f)
        self.dl_frame.pack(fill="x", **pad)
        tk.Label(self.dl_frame, text="Save to:").pack(side="left")
        self.dl_label = tk.Label(self.dl_frame, text=self.download_dir, fg="blue")
        self.dl_label.pack(side="left", padx=8)
        tk.Button(self.dl_frame, text="Change...", command=self._choose_download_dir).pack(side="right")
        self._toggle_mode()

        # VLC path row
        vlc_frame = tk.Frame(f)
        vlc_frame.pack(fill="x", **pad)
        tk.Label(vlc_frame, text="VLC path:").pack(side="left")
        self.vlc_label = tk.Label(vlc_frame, text=self.vlc_path or "NOT FOUND — click Browse",
                                   fg="green" if self.vlc_path else "red")
        self.vlc_label.pack(side="left", padx=8)
        tk.Button(vlc_frame, text="Browse...", command=self._browse_vlc).pack(side="right")

        self.go_button = tk.Button(f, text="Go", command=self._on_go, height=2)
        self.go_button.pack(fill="x", **pad)

        tk.Label(f, text="Log:").pack(anchor="w", **pad)
        self.log_box = tk.Text(f, height=12, state="disabled", bg="#111", fg="#ddd")
        self.log_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        if yt_dlp is None:
            self.log("WARNING: yt-dlp is not installed. Run: pip install yt-dlp")

    def _toggle_mode(self):
        if self.mode_var.get() == "download":
            for child in self.dl_frame.winfo_children():
                child.configure(state="normal")
        else:
            pass  # folder chooser stays visible either way; harmless if unused

    def _choose_download_dir(self):
        path = filedialog.askdirectory(title="Choose download folder", initialdir=self.download_dir)
        if path:
            self.download_dir = path
            self.dl_label.config(text=path)

    def _browse_vlc(self):
        path = filedialog.askopenfilename(title="Select VLC executable")
        if path:
            self.vlc_path = path
            self.vlc_label.config(text=path, fg="green")

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _on_go(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Paste a YouTube URL first.")
            return
        if not self.vlc_path:
            messagebox.showerror("VLC not found", "Locate your VLC executable via Browse.")
            return

        self.go_button.config(state="disabled", text="Working...")
        mode = self.mode_var.get()
        thread = threading.Thread(target=self._worker, args=(url, mode), daemon=True)
        thread.start()

    def _worker(self, url, mode):
        try:
            if mode == "stream":
                entries = resolve_urls(url, self.log)
                launch_vlc(self.vlc_path, entries, self.log)
                for title, _ in entries:
                    add_history_entry(title, url, "streamed")
            else:
                downloaded = download_locally(url, self.download_dir, self.log)
                if not downloaded:
                    raise RuntimeError("Nothing downloaded successfully.")
                for title, path in downloaded:
                    add_history_entry(title, url, "downloaded", file_path=path)
                self.log(f"Downloaded {len(downloaded)} item(s). Opening in VLC...")
                launch_vlc(self.vlc_path, downloaded, self.log)

            self.log("Done.")
            self.root.after(0, self._refresh_history)
        except Exception as e:
            self.log(f"ERROR: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            self.root.after(0, lambda: self.go_button.config(state="normal", text="Go"))

    # -------------------- History tab --------------------

    def _build_history_tab(self):
        pad = {"padx": 12, "pady": 6}
        f = self.history_tab

        columns = ("timestamp", "title", "kind")
        self.tree = ttk.Treeview(f, columns=columns, show="headings", height=18)
        self.tree.heading("timestamp", text="When")
        self.tree.heading("title", text="Title")
        self.tree.heading("kind", text="Type")
        self.tree.column("timestamp", width=150)
        self.tree.column("title", width=320)
        self.tree.column("kind", width=100)
        self.tree.pack(fill="both", expand=True, **pad)

        btn_frame = tk.Frame(f)
        btn_frame.pack(fill="x", **pad)
        tk.Button(btn_frame, text="Play selected", command=self._play_selected).pack(side="left")
        tk.Button(btn_frame, text="Open containing folder", command=self._open_selected_folder).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Refresh", command=self._refresh_history).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Clear history", command=self._clear_history).pack(side="right")

        self._history_data = []

    def _refresh_history(self):
        self._history_data = load_history()
        self.tree.delete(*self.tree.get_children())
        for i, entry in enumerate(self._history_data):
            ts = entry.get("timestamp", "")
            self.tree.insert("", "end", iid=str(i),
                              values=(ts, entry.get("title", "Unknown"), entry.get("kind", "")))

    def _get_selected_entry(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Select a history entry first.")
            return None
        idx = int(sel[0])
        return self._history_data[idx]

    def _play_selected(self):
        entry = self._get_selected_entry()
        if not entry:
            return
        if not self.vlc_path:
            messagebox.showerror("VLC not found", "Locate VLC in the Play tab first.")
            return

        if entry["kind"] == "downloaded" and entry.get("file_path") and os.path.isfile(entry["file_path"]):
            subprocess.Popen([self.vlc_path, entry["file_path"]])
        else:
            # Re-resolve a stream link (original stream URLs expire)
            self.log_if_possible(f"Re-resolving stream for: {entry['title']}")
            def redo():
                try:
                    entries = resolve_urls(entry["source_url"], lambda m: None)
                    match = next((e for e in entries if e[0] == entry["title"]), entries[0] if entries else None)
                    if match:
                        subprocess.Popen([self.vlc_path, match[1]])
                    else:
                        messagebox.showerror("Error", "Could not re-resolve this video.")
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            threading.Thread(target=redo, daemon=True).start()

    def log_if_possible(self, msg):
        try:
            self.log(msg)
        except Exception:
            pass

    def _open_selected_folder(self):
        entry = self._get_selected_entry()
        if not entry:
            return
        path = entry.get("file_path")
        if not path or not os.path.isfile(path):
            messagebox.showinfo("Not downloaded", "This entry was streamed, not downloaded — no local file.")
            return
        folder = os.path.dirname(path)
        if sys.platform.startswith("win"):
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    def _clear_history(self):
        if messagebox.askyesno("Clear history", "Delete all watch history? (Downloaded files are kept.)"):
            save_history([])
            self._refresh_history()


def main():
    root = tk.Tk()
    app = YtVlcApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
