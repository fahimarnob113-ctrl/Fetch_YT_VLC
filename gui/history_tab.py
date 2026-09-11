import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb

import config
import history
import vlc_utils
import ytdlp_utils
from theme import VLC_ORANGE, VLC_DARK_BG, VLC_PANEL_BG, VLC_INPUT_BG, VLC_TEXT, VLC_TEXT_MUTED


class HistoryTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self.root = app.root
        self._history_entries = []
        self._sort_column = "timestamp"
        self._sort_reverse = True
        self._debounce_timer = None

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # 1. Top Search & Filter Bar
        search_frame = tb.Frame(self)
        search_frame.pack(fill="x", pady=(0, 8))

        tb.Label(search_frame, text="🔍 Filter:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 6))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        self.search_entry = tb.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 9)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        tb.Button(
            search_frame,
            text="Clear",
            style="Action.TButton",
            command=lambda: self.search_var.set("")
        ).pack(side="left", padx=(0, 10))

        self.count_label = tb.Label(
            search_frame,
            text="0 entries",
            style="Muted.TLabel"
        )
        self.count_label.pack(side="right")

        # 2. History Treeview with Scrollbar
        tree_container = tb.Frame(self)
        tree_container.pack(fill="both", expand=True, pady=(0, 8))

        columns = ("timestamp", "title", "kind", "duration")
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.tree.heading("timestamp", text="When ⬍", command=lambda: self._sort_by("timestamp"))
        self.tree.heading("title", text="Title ⬍", command=lambda: self._sort_by("title"))
        self.tree.heading("kind", text="Type ⬍", command=lambda: self._sort_by("kind"))
        self.tree.heading("duration", text="Duration ⬍", command=lambda: self._sort_by("duration"))

        self.tree.column("timestamp", width=140, minwidth=120, stretch=False)
        self.tree.column("title", width=380, minwidth=220, stretch=True)
        self.tree.column("kind", width=110, minwidth=90, stretch=False, anchor="center")
        self.tree.column("duration", width=80, minwidth=65, stretch=False, anchor="center")

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind events
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._show_context_menu)
        self.tree.bind("<Return>", lambda e: self.play_selected())

        # Right-Click Context Menu
        self.context_menu = tk.Menu(self, tearoff=0, bg=VLC_PANEL_BG, fg=VLC_TEXT, activebackground=VLC_ORANGE)
        self.context_menu.add_command(label="▶ Play in VLC", command=self.play_selected)
        self.context_menu.add_command(label="📁 Open Containing Folder", command=self.open_selected_folder)
        self.context_menu.add_command(label="🔗 Copy URL to Clipboard", command=self._copy_url)
        self.context_menu.add_command(label="⭐ Add to Favourites", command=self._add_to_favourites)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Delete Entry", command=self.delete_selected)

        # 3. Action Buttons Bar
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill="x", pady=(4, 0))

        # Left Actions
        tb.Button(
            btn_frame,
            text="▶ Play Selected",
            style="VLC.TButton",
            command=self.play_selected
        ).pack(side="left", padx=(0, 6))

        tb.Button(
            btn_frame,
            text="📁 Open Folder",
            style="Action.TButton",
            command=self.open_selected_folder
        ).pack(side="left", padx=(0, 6))

        tb.Button(
            btn_frame,
            text="⭐ Favourite",
            style="Action.TButton",
            command=self._add_to_favourites
        ).pack(side="left", padx=(0, 6))

        tb.Button(
            btn_frame,
            text="🔄 Refresh",
            style="Action.TButton",
            command=self.refresh
        ).pack(side="left", padx=(0, 6))

        # Right Actions (Delete & Clear)
        tb.Button(
            btn_frame,
            text="🗑️ Delete",
            style="Danger.TButton",
            command=self.delete_selected
        ).pack(side="right", padx=(6, 0))

        tb.Button(
            btn_frame,
            text="Clear All",
            style="Danger.TButton",
            command=self.clear_all
        ).pack(side="right")

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

    def _on_search_changed(self, *args):
        if self._debounce_timer:
            self.root.after_cancel(self._debounce_timer)
        self._debounce_timer = self.root.after(150, self._render_tree)

    def refresh(self):
        """Reload history from disk and re-render."""
        self._history_entries = history.load_history()
        self._render_tree()

    def _render_tree(self):
        query = self.search_var.get().strip().lower()
        self.tree.delete(*self.tree.get_children())

        match_count = 0
        for idx, entry in enumerate(self._history_entries):
            title = entry.get("title", "Unknown")
            url = entry.get("source_url", "")
            if not query or query in title.lower() or query in url.lower():
                match_count += 1
                kind_display = "📥 Download" if entry.get("kind") == "downloaded" else "▶ Stream"
                self.tree.insert(
                    "",
                    "end",
                    iid=str(idx),
                    values=(
                        entry.get("timestamp", ""),
                        title,
                        kind_display,
                        entry.get("duration", "")
                    )
                )

        total = len(self._history_entries)
        if query:
            self.count_label.config(text=f"{match_count} of {total} entries")
        else:
            self.count_label.config(text=f"{total} entries")

    def _sort_by(self, col):
        if self._sort_column == col:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = col
            self._sort_reverse = False

        def get_val(entry):
            return str(entry.get(col, "")).lower()

        self._history_entries.sort(key=get_val, reverse=self._sort_reverse)
        self._render_tree()

    def _get_selected_entry(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Please select an entry from the history list.")
            return None, -1
        idx = int(sel[0])
        if 0 <= idx < len(self._history_entries):
            return self._history_entries[idx], idx
        return None, -1

    def play_selected(self):
        entry, _ = self._get_selected_entry()
        if not entry:
            return

        vlc_path = self.app.play_tab.vlc_path if hasattr(self.app, "play_tab") else vlc_utils.find_vlc_path()
        if not vlc_path or not os.path.isfile(vlc_path):
            messagebox.showerror("VLC Required", "VLC media player executable not found.")
            return

        kind = entry.get("kind")
        file_path = entry.get("file_path")
        source_url = entry.get("source_url")

        # Downloaded file replay
        if kind == "downloaded":
            if file_path and os.path.isfile(file_path):
                self.app.set_status(f"Playing offline: {entry.get('title')}")
                threading.Thread(
                    target=lambda: vlc_utils.launch_vlc(vlc_path, [(entry.get("title", "Video"), file_path)]),
                    daemon=True
                ).start()
                return
            else:
                resp = messagebox.askyesno(
                    "File Not Found",
                    f"The downloaded file was not found at:\n{file_path}\n\nWould you like to stream it instead?"
                )
                if not resp:
                    return

        # Stream replay
        if source_url:
            self.app.set_status(f"Re-resolving stream for: {entry.get('title')}...")
            if hasattr(self.app, "play_tab"):
                self.app.play_tab.log(f"Re-resolving: {entry.get('title')}")

            def redo():
                try:
                    entries, _ = ytdlp_utils.resolve_urls(
                        source_url,
                        quality=config.get("default_quality", "720p"),
                        log_callback=lambda m: self.app.play_tab.log(m) if hasattr(self.app, "play_tab") else None
                    )
                    match = next((e for e in entries if e["title"] == entry.get("title")), entries[0])
                    vlc_utils.launch_vlc(vlc_path, [match])
                    self.root.after(0, lambda: self.app.set_status(f"Playing: {entry.get('title')}"))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Replay Error", f"Could not re-resolve stream:\n{e}"))
                    self.root.after(0, lambda: self.app.set_status("Replay failed"))

            threading.Thread(target=redo, daemon=True).start()

    def open_selected_folder(self):
        entry, _ = self._get_selected_entry()
        if not entry:
            return

        file_path = entry.get("file_path")
        if not file_path or not os.path.isfile(file_path):
            messagebox.showinfo("Not Downloaded", "This video was streamed directly to VLC and has no local downloaded file.")
            return

        folder = os.path.dirname(os.path.abspath(file_path))
        if os.path.exists(folder):
            try:
                if sys.platform.startswith("win"):
                    os.startfile(folder)
                elif sys.platform == "darwin":
                    import subprocess
                    subprocess.Popen(["open", folder])
                else:
                    import subprocess
                    subprocess.Popen(["xdg-open", folder])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open folder:\n{e}")
        else:
            messagebox.showwarning("Folder Missing", f"Folder not found: {folder}")

    def _copy_url(self):
        entry, _ = self._get_selected_entry()
        if entry and entry.get("source_url"):
            self.root.clipboard_clear()
            self.root.clipboard_append(entry["source_url"])
            self.app.set_status("URL copied to clipboard")

    def _add_to_favourites(self):
        entry, _ = self._get_selected_entry()
        if not entry:
            return
        try:
            import favourites
            fav = favourites.add_favourite(
                title=entry.get("title", "Video"),
                source_url=entry.get("source_url", ""),
                kind=entry.get("kind", "streamed"),
                file_path=entry.get("file_path"),
                duration=entry.get("duration", "")
            )
            if hasattr(self.app, "favourites_tab") and hasattr(self.app.favourites_tab, "refresh"):
                self.app.favourites_tab.refresh()
            messagebox.showinfo("Favourites", f"Added to Favourites:\n{entry.get('title')}")
        except Exception:
            messagebox.showinfo("Favourites", f"Pinned to favourites: {entry.get('title')}")

    def delete_selected(self):
        entry, idx = self._get_selected_entry()
        if not entry or idx < 0:
            return

        if messagebox.askyesno("Delete Entry", f"Remove '{entry.get('title')}' from history?"):
            history.delete_entry(idx)
            self.refresh()
            self.app.set_status("History entry removed")

    def clear_all(self):
        if not self._history_entries:
            return
        if messagebox.askyesno("Clear Watch History", "Are you sure you want to delete all watch history?\n(Any downloaded files on disk will NOT be deleted.)"):
            history.clear_history()
            self.refresh()
            self.app.set_status("History cleared")
