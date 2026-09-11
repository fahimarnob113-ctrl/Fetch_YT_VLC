import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb

import config
import favourites
import vlc_utils
import ytdlp_utils
from theme import VLC_ORANGE, VLC_PANEL_BG, VLC_TEXT, VLC_TEXT_MUTED


class FavouritesTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self.root = app.root
        self._items = []

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # 1. Quick Add Section
        add_frame = tb.LabelFrame(self, text=" ⭐ Pin a New Video / Playlist to Favourites ", padding=(10, 8))
        add_frame.pack(fill="x", pady=(0, 10))

        entry_box = tb.Frame(add_frame)
        entry_box.pack(fill="x")

        self.url_var = tk.StringVar()
        self.url_entry = tb.Entry(
            entry_box,
            textvariable=self.url_var,
            font=("Segoe UI", 9)
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.url_entry.bind("<Return>", lambda e: self._add_manual_url())

        tb.Button(
            entry_box,
            text="📋 Paste",
            style="Action.TButton",
            command=self._paste_url
        ).pack(side="left", padx=(0, 4))

        self.add_btn = tb.Button(
            entry_box,
            text="+ Pin Video",
            style="VLC.TButton",
            command=self._add_manual_url
        )
        self.add_btn.pack(side="left", padx=(0, 10))

        self.fav_count_label = tb.Label(
            entry_box,
            text="0 pinned",
            style="Muted.TLabel"
        )
        self.fav_count_label.pack(side="right")

        # 2. Favourites Treeview
        self.tree_container = tb.Frame(self)
        self.tree_container.pack(fill="both", expand=True, pady=(0, 8))

        columns = ("title", "kind", "duration", "added_at")
        self.tree = ttk.Treeview(
            self.tree_container,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        from theme import setup_treeview_tags
        setup_treeview_tags(self.tree)

        self.tree.heading("title", text="Title")
        self.tree.heading("kind", text="Type")
        self.tree.heading("duration", text="Duration")
        self.tree.heading("added_at", text="Pinned On")

        self.tree.column("title", width=420, minwidth=240, stretch=True)
        self.tree.column("kind", width=110, minwidth=90, stretch=False, anchor="center")
        self.tree.column("duration", width=80, minwidth=65, stretch=False, anchor="center")
        self.tree.column("added_at", width=140, minwidth=120, stretch=False, anchor="center")

        self.scrollbar = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Empty State Placeholder Frame
        self.empty_frame = tb.Frame(self.tree_container)
        tb.Label(self.empty_frame, text="⭐", font=("Segoe UI", 36)).pack(pady=(30, 8))
        tb.Label(self.empty_frame, text="No Favourites Pinned Yet", font=("Segoe UI", 12, "bold"), foreground=VLC_ORANGE).pack(pady=(0, 4))
        tb.Label(
            self.empty_frame,
            text="Pin your favourite videos from Watch History or paste any link above.\nQuickly reorder items using Move Up / Down.",
            font=("Segoe UI", 9),
            style="Muted.TLabel",
            justify="center"
        ).pack(pady=(0, 20))

        # Bind events
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._show_context_menu)
        self.tree.bind("<Return>", lambda e: self.play_selected())

        # Right-Click Context Menu
        self.context_menu = tk.Menu(self, tearoff=0, bg=VLC_PANEL_BG, fg=VLC_TEXT, activebackground=VLC_ORANGE)
        self.context_menu.add_command(label="▶ Play in VLC", command=self.play_selected)
        self.context_menu.add_command(label="▲ Move Up", command=self.move_up)
        self.context_menu.add_command(label="▼ Move Down", command=self.move_down)
        self.context_menu.add_command(label="📁 Open Containing Folder", command=self.open_selected_folder)
        self.context_menu.add_command(label="🔗 Copy URL", command=self._copy_url)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Remove from Favourites", command=self.remove_selected)

        # 3. Action Buttons Bar
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill="x", pady=(4, 6))

        # Left Actions
        tb.Button(
            btn_frame,
            text="▶ Play Selected",
            style="VLC.TButton",
            command=self.play_selected
        ).pack(side="left", padx=(0, 6))

        tb.Button(
            btn_frame,
            text="▲ Move Up",
            style="Action.TButton",
            command=self.move_up
        ).pack(side="left", padx=(0, 4))

        tb.Button(
            btn_frame,
            text="▼ Move Down",
            style="Action.TButton",
            command=self.move_down
        ).pack(side="left", padx=(0, 6))

        tb.Button(
            btn_frame,
            text="📁 Open Folder",
            style="Action.TButton",
            command=self.open_selected_folder
        ).pack(side="left", padx=(0, 6))

        tb.Button(
            btn_frame,
            text="🔄 Refresh",
            style="Action.TButton",
            command=self.refresh
        ).pack(side="left", padx=(0, 6))

        # Right Action (Remove)
        tb.Button(
            btn_frame,
            text="🗑️ Remove",
            style="Danger.TButton",
            command=self.remove_selected
        ).pack(side="right")

        # 4. Cheatsheet Tip Bar
        tip_bar = tb.Frame(self)
        tip_bar.pack(fill="x", side="bottom")
        tb.Label(
            tip_bar,
            text="💡 Double-click any favourite to play in VLC  •  Use Move Up / Down to order your list",
            font=("Segoe UI", 8),
            style="Muted.TLabel"
        ).pack(side="left")

    def _paste_url(self):
        try:
            txt = self.root.clipboard_get()
            if txt:
                self.url_var.set(txt.strip())
        except Exception:
            pass

    def _add_manual_url(self):
        raw_url = self.url_var.get().strip()
        is_valid, err = ytdlp_utils.validate_url(raw_url)
        if not is_valid:
            messagebox.showwarning("Invalid URL", err)
            return

        self.add_btn.config(state="disabled", text="⏳ Adding...")
        self.app.set_status("Fetching title for favourite...")

        def fetch():
            try:
                entries, meta = ytdlp_utils.resolve_urls(
                    raw_url,
                    quality="720p",
                    log_callback=lambda m: self.app.play_tab.log(m) if hasattr(self.app, "play_tab") else None
                )
                title = meta.get("title") or (entries[0]["title"] if entries else "Video")
                dur = entries[0].get("duration", "") if entries else ""

                favourites.add_favourite(
                    title=title,
                    source_url=raw_url,
                    kind="streamed",
                    duration=dur
                )
                self.root.after(0, lambda: [
                    self.url_var.set(""),
                    self.refresh(),
                    self.app.set_status(f"Added to favourites: {title}")
                ])
            except Exception as e:
                # Fallback: add with URL as title
                favourites.add_favourite(title=raw_url, source_url=raw_url, kind="streamed")
                self.root.after(0, lambda: [
                    self.url_var.set(""),
                    self.refresh(),
                    self.app.set_status("Added URL to favourites")
                ])
            finally:
                self.root.after(0, lambda: self.add_btn.config(state="normal", text="+ Pin Video"))

        threading.Thread(target=fetch, daemon=True).start()

    def _on_double_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.play_selected()

    def _show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def refresh(self):
        """Reload favourites and re-render."""
        self._items = favourites.load_favourites()
        self.tree.delete(*self.tree.get_children())
        total = len(self._items)
        if total == 0:
            self.tree.pack_forget()
            self.scrollbar.pack_forget()
            self.empty_frame.pack(fill="both", expand=True)
            self.fav_count_label.config(text="0 pinned")
        else:
            self.empty_frame.pack_forget()
            if not self.tree.winfo_ismapped():
                self.tree.pack(side="left", fill="both", expand=True)
                self.scrollbar.pack(side="right", fill="y")
            self.fav_count_label.config(text=f"{total} pinned")
            for idx, item in enumerate(self._items):
                kind = item.get("kind", "streamed")
                kind_str = "📥 Downloaded" if kind == "downloaded" else "▶ Streamed"
                tag = "downloaded" if kind == "downloaded" else "streamed"
                self.tree.insert(
                    "",
                    "end",
                    iid=str(idx),
                    values=(
                        item.get("title", "Unknown"),
                        kind_str,
                        item.get("duration", ""),
                        item.get("added_at", "")
                    ),
                    tags=(tag,)
                )

    def _get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Please select a favourite from the list.")
            return None, -1
        idx = int(sel[0])
        if 0 <= idx < len(self._items):
            return self._items[idx], idx
        return None, -1

    def play_selected(self):
        item, _ = self._get_selected()
        if not item:
            return

        vlc_path = self.app.play_tab.vlc_path if hasattr(self.app, "play_tab") else vlc_utils.find_vlc_path()
        if not vlc_path or not os.path.isfile(vlc_path):
            messagebox.showerror("VLC Required", "VLC executable not found.")
            return

        kind = item.get("kind")
        file_path = item.get("file_path")
        source_url = item.get("source_url")

        # Offline local file
        if kind == "downloaded" and file_path and os.path.isfile(file_path):
            self.app.set_status(f"Playing favourite: {item.get('title')}")
            threading.Thread(
                target=lambda: vlc_utils.launch_vlc(vlc_path, [(item.get("title", "Video"), file_path)]),
                daemon=True
            ).start()
            return

        # Stream link
        if source_url:
            self.app.set_busy(True, f"Resolving favourite: {item.get('title')}...")
            if hasattr(self.app, "play_tab"):
                self.app.play_tab.log(f"Resolving favourite: {item.get('title')}")

            def redo():
                try:
                    entries, _ = ytdlp_utils.resolve_urls(
                        source_url,
                        quality=config.get("default_quality", "720p"),
                        log_callback=lambda m: self.app.play_tab.log(m) if hasattr(self.app, "play_tab") else None
                    )
                    match = next((e for e in entries if e["title"] == item.get("title")), entries[0])
                    vlc_utils.launch_vlc(vlc_path, [match])
                    self.root.after(0, lambda: self.app.set_busy(False, f"Playing: {item.get('title')}"))
                except Exception as e:
                    self.root.after(0, lambda: [
                        messagebox.showerror("Playback Error", f"Could not stream favourite:\n{e}"),
                        self.app.set_busy(False, "Playback failed")
                    ])

            threading.Thread(target=redo, daemon=True).start()

    def move_up(self):
        _, idx = self._get_selected()
        if idx > 0:
            favourites.move_favourite(idx, idx - 1)
            self.refresh()
            self.tree.selection_set(str(idx - 1))

    def move_down(self):
        _, idx = self._get_selected()
        if idx >= 0 and idx < len(self._items) - 1:
            favourites.move_favourite(idx, idx + 1)
            self.refresh()
            self.tree.selection_set(str(idx + 1))

    def open_selected_folder(self):
        item, _ = self._get_selected()
        if not item:
            return

        file_path = item.get("file_path")
        if not file_path or not os.path.isfile(file_path):
            messagebox.showinfo("Not Downloaded", "This favourite was streamed directly and has no local downloaded file.")
            return

        folder = os.path.dirname(os.path.abspath(file_path))
        if os.path.exists(folder):
            if sys.platform.startswith("win"):
                os.startfile(folder)
            else:
                import subprocess
                subprocess.Popen(["xdg-open", folder])

    def _copy_url(self):
        item, _ = self._get_selected()
        if item and item.get("source_url"):
            self.root.clipboard_clear()
            self.root.clipboard_append(item["source_url"])
            self.app.set_status("URL copied to clipboard")

    def remove_selected(self):
        item, idx = self._get_selected()
        if not item or idx < 0:
            return

        if messagebox.askyesno("Remove Favourite", f"Remove '{item.get('title')}' from favourites?"):
            favourites.remove_favourite(idx)
            self.refresh()
            self.app.set_status("Removed from favourites")
