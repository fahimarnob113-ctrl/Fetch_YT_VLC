import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import ttkbootstrap as tb

import config
import playlists
import vlc_utils
import ytdlp_utils
from theme import VLC_ORANGE, VLC_PANEL_BG, VLC_TEXT, VLC_TEXT_MUTED


class PlaylistsTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self.root = app.root
        self._playlists = []
        self._selected_playlist_id = None

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # 1. Top URL Importer Bar
        import_frame = tb.LabelFrame(self, text=" 🔗 Fetch & Save a YouTube Playlist ", padding=(10, 8))
        import_frame.pack(fill="x", pady=(0, 10))

        url_box = tb.Frame(import_frame)
        url_box.pack(fill="x")

        self.url_var = tk.StringVar()
        self.url_entry = tb.Entry(
            url_box,
            textvariable=self.url_var,
            font=("Segoe UI", 9)
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.url_entry.bind("<Return>", lambda e: self._fetch_playlist_url())

        tb.Button(
            url_box,
            text="Paste",
            style="Action.TButton",
            command=self._paste_url
        ).pack(side="left", padx=(0, 4))

        self.fetch_btn = tb.Button(
            url_box,
            text="📥 Fetch & Save Playlist",
            style="VLC.TButton",
            command=self._fetch_playlist_url
        )
        self.fetch_btn.pack(side="left")

        # 2. Split Paned Window (Left: Playlists, Right: Tracks)
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, pady=(0, 8))

        # --- Left Panel: Playlists List ---
        left_frame = tb.Frame(paned, padding=(0, 0, 8, 0))
        paned.add(left_frame, weight=1)

        left_hdr = tb.Frame(left_frame)
        left_hdr.pack(fill="x", pady=(0, 4))
        tb.Label(left_hdr, text="📁 Playlists", font=("Segoe UI", 10, "bold")).pack(side="left")

        pl_tree_box = tb.Frame(left_frame)
        pl_tree_box.pack(fill="both", expand=True, pady=(0, 6))

        self.pl_tree = ttk.Treeview(
            pl_tree_box,
            columns=("name", "count"),
            show="headings",
            selectmode="browse"
        )
        self.pl_tree.heading("name", text="Playlist")
        self.pl_tree.heading("count", text="Tracks")
        self.pl_tree.column("name", width=160, stretch=True)
        self.pl_tree.column("count", width=60, stretch=False, anchor="center")

        pl_scroll = ttk.Scrollbar(pl_tree_box, orient="vertical", command=self.pl_tree.yview)
        self.pl_tree.configure(yscrollcommand=pl_scroll.set)
        self.pl_tree.pack(side="left", fill="both", expand=True)
        pl_scroll.pack(side="right", fill="y")

        self.pl_tree.bind("<<TreeviewSelect>>", self._on_playlist_select)

        # Left panel controls
        pl_btns = tb.Frame(left_frame)
        pl_btns.pack(fill="x")

        tb.Button(
            pl_btns,
            text="+ New",
            style="Action.TButton",
            command=self._new_playlist
        ).pack(side="left", padx=(0, 4))

        tb.Button(
            pl_btns,
            text="✏️ Rename",
            style="Action.TButton",
            command=self._rename_playlist
        ).pack(side="left", padx=(0, 4))

        tb.Button(
            pl_btns,
            text="🗑️ Delete",
            style="Danger.TButton",
            command=self._delete_playlist
        ).pack(side="right")

        # --- Right Panel: Selected Playlist Tracks ---
        right_frame = tb.Frame(paned, padding=(8, 0, 0, 0))
        paned.add(right_frame, weight=3)

        right_hdr = tb.Frame(right_frame)
        right_hdr.pack(fill="x", pady=(0, 4))

        self.details_title = tb.Label(
            right_hdr,
            text="No playlist selected",
            font=("Segoe UI", 10, "bold"),
            foreground=VLC_ORANGE
        )
        self.details_title.pack(side="left")

        self.details_count = tb.Label(
            right_hdr,
            text="",
            style="Muted.TLabel"
        )
        self.details_count.pack(side="right")

        tracks_box = tb.Frame(right_frame)
        tracks_box.pack(fill="both", expand=True, pady=(0, 6))

        self.tracks_tree = ttk.Treeview(
            tracks_box,
            columns=("index", "title", "duration"),
            show="headings",
            selectmode="browse"
        )
        self.tracks_tree.heading("index", text="#")
        self.tracks_tree.heading("title", text="Video Title")
        self.tracks_tree.heading("duration", text="Duration")

        self.tracks_tree.column("index", width=40, stretch=False, anchor="center")
        self.tracks_tree.column("title", width=380, stretch=True)
        self.tracks_tree.column("duration", width=80, stretch=False, anchor="center")

        tr_scroll = ttk.Scrollbar(tracks_box, orient="vertical", command=self.tracks_tree.yview)
        self.tracks_tree.configure(yscrollcommand=tr_scroll.set)
        self.tracks_tree.pack(side="left", fill="both", expand=True)
        tr_scroll.pack(side="right", fill="y")

        self.tracks_tree.bind("<Double-1>", lambda e: self.play_selected_track())
        self.tracks_tree.bind("<Return>", lambda e: self.play_selected_track())

        # Right panel action buttons
        tr_btns = tb.Frame(right_frame)
        tr_btns.pack(fill="x")

        tb.Button(
            tr_btns,
            text="▶ Play All in VLC",
            style="VLC.TButton",
            command=self.play_all_in_vlc
        ).pack(side="left", padx=(0, 6))

        tb.Button(
            tr_btns,
            text="▶ Play Track",
            style="Action.TButton",
            command=self.play_selected_track
        ).pack(side="left", padx=(0, 6))

        tb.Button(
            tr_btns,
            text="🔄 Refresh",
            style="Action.TButton",
            command=self.refresh
        ).pack(side="left", padx=(0, 6))

        tb.Button(
            tr_btns,
            text="🗑️ Remove Track",
            style="Danger.TButton",
            command=self._remove_track
        ).pack(side="right")

    def _paste_url(self):
        try:
            txt = self.root.clipboard_get()
            if txt:
                self.url_var.set(txt.strip())
        except Exception:
            pass

    def _fetch_playlist_url(self):
        raw_url = self.url_var.get().strip()
        is_valid, err = ytdlp_utils.validate_url(raw_url)
        if not is_valid:
            messagebox.showwarning("Invalid URL", err)
            return

        self.fetch_btn.config(state="disabled", text="⏳ Resolving...")
        self.app.set_status("Fetching playlist tracks from YouTube...")

        def worker():
            try:
                entries, meta = ytdlp_utils.resolve_urls(
                    raw_url,
                    quality="720p",
                    log_callback=lambda m: self.app.play_tab.log(m) if hasattr(self.app, "play_tab") else None
                )
                pl_name = meta.get("playlist_title") or meta.get("title") or "YouTube Playlist"
                pl = playlists.create_playlist(name=pl_name, source_url=raw_url, items=entries)

                self.root.after(0, lambda: [
                    self.url_var.set(""),
                    self.refresh(),
                    self._select_playlist_by_id(pl["id"]),
                    self.app.set_status(f"Saved playlist: {pl_name} ({len(entries)} items)")
                ])
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fetch Error", f"Could not fetch playlist:\n{e}"))
                self.root.after(0, lambda: self.app.set_status("Playlist fetch failed"))
            finally:
                self.root.after(0, lambda: self.fetch_btn.config(state="normal", text="📥 Fetch & Save Playlist"))

        threading.Thread(target=worker, daemon=True).start()

    def refresh(self):
        """Reload playlists from disk and render."""
        self._playlists = playlists.load_playlists()
        self.pl_tree.delete(*self.pl_tree.get_children())

        for pl in self._playlists:
            track_count = len(pl.get("items", []))
            self.pl_tree.insert(
                "",
                "end",
                iid=pl["id"],
                values=(pl.get("name", "Untitled"), f"{track_count} tracks")
            )

        if self._selected_playlist_id:
            if any(p["id"] == self._selected_playlist_id for p in self._playlists):
                self.pl_tree.selection_set(self._selected_playlist_id)
                self._load_tracks_for_playlist(self._selected_playlist_id)
            else:
                self._clear_tracks_view()
        elif self._playlists:
            first_id = self._playlists[0]["id"]
            self.pl_tree.selection_set(first_id)
            self._load_tracks_for_playlist(first_id)
        else:
            self._clear_tracks_view()

    def _select_playlist_by_id(self, pl_id):
        self._selected_playlist_id = pl_id
        if pl_id in self.pl_tree.get_children():
            self.pl_tree.selection_set(pl_id)
            self._load_tracks_for_playlist(pl_id)

    def _on_playlist_select(self, event):
        sel = self.pl_tree.selection()
        if sel:
            self._selected_playlist_id = sel[0]
            self._load_tracks_for_playlist(sel[0])

    def _load_tracks_for_playlist(self, pl_id):
        pl = playlists.get_playlist(pl_id)
        if not pl:
            self._clear_tracks_view()
            return

        self._selected_playlist_id = pl_id
        items = pl.get("items", [])
        self.details_title.config(text=pl.get("name", "Playlist"))
        self.details_count.config(text=f"{len(items)} tracks")

        self.tracks_tree.delete(*self.tracks_tree.get_children())
        for idx, it in enumerate(items):
            self.tracks_tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(
                    it.get("index", idx + 1),
                    it.get("title", "Unknown Track"),
                    it.get("duration", "")
                )
            )

    def _clear_tracks_view(self):
        self.details_title.config(text="No playlist selected")
        self.details_count.config(text="")
        self.tracks_tree.delete(*self.tracks_tree.get_children())

    def _new_playlist(self):
        name = simpledialog.askstring("New Playlist", "Enter a name for the new playlist:")
        if name and name.strip():
            pl = playlists.create_playlist(name=name.strip())
            self.refresh()
            self._select_playlist_by_id(pl["id"])

    def _rename_playlist(self):
        if not self._selected_playlist_id:
            messagebox.showinfo("No Selection", "Please select a playlist to rename.")
            return

        pl = playlists.get_playlist(self._selected_playlist_id)
        if not pl:
            return

        new_name = simpledialog.askstring("Rename Playlist", "Enter new name:", initialvalue=pl.get("name", ""))
        if new_name and new_name.strip():
            playlists.rename_playlist(self._selected_playlist_id, new_name.strip())
            self.refresh()

    def _delete_playlist(self):
        if not self._selected_playlist_id:
            messagebox.showinfo("No Selection", "Please select a playlist to delete.")
            return

        pl = playlists.get_playlist(self._selected_playlist_id)
        if not pl:
            return

        if messagebox.askyesno("Delete Playlist", f"Delete the playlist '{pl.get('name')}' permanently?"):
            playlists.delete_playlist(self._selected_playlist_id)
            self._selected_playlist_id = None
            self.refresh()

    def _remove_track(self):
        if not self._selected_playlist_id:
            return
        sel = self.tracks_tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Please select a track to remove.")
            return

        track_idx = int(sel[0])
        playlists.remove_item_from_playlist(self._selected_playlist_id, track_idx)
        self.refresh()

    def play_all_in_vlc(self):
        if not self._selected_playlist_id:
            messagebox.showinfo("No Playlist", "Please select a playlist to play.")
            return

        pl = playlists.get_playlist(self._selected_playlist_id)
        if not pl or not pl.get("items"):
            messagebox.showwarning("Empty Playlist", "This playlist has no tracks to play.")
            return

        vlc_path = self.app.play_tab.vlc_path if hasattr(self.app, "play_tab") else vlc_utils.find_vlc_path()
        if not vlc_path or not os.path.isfile(vlc_path):
            messagebox.showerror("VLC Required", "VLC media player executable not found.")
            return

        items = pl.get("items", [])
        self.app.set_status(f"Opening playlist in VLC: {pl.get('name')} ({len(items)} items)...")

        # Launch VLC asynchronously with M3U playlist
        threading.Thread(
            target=lambda: vlc_utils.launch_vlc(vlc_path, items),
            daemon=True
        ).start()

    def play_selected_track(self):
        if not self._selected_playlist_id:
            return
        sel = self.tracks_tree.selection()
        if not sel:
            messagebox.showinfo("No Track", "Please select a track to play.")
            return

        pl = playlists.get_playlist(self._selected_playlist_id)
        if not pl or not pl.get("items"):
            return

        track_idx = int(sel[0])
        if 0 <= track_idx < len(pl["items"]):
            item = pl["items"][track_idx]
            vlc_path = self.app.play_tab.vlc_path if hasattr(self.app, "play_tab") else vlc_utils.find_vlc_path()
            if not vlc_path or not os.path.isfile(vlc_path):
                messagebox.showerror("VLC Required", "VLC executable not found.")
                return

            self.app.set_status(f"Playing track in VLC: {item.get('title')}")
            threading.Thread(
                target=lambda: vlc_utils.launch_vlc(vlc_path, [item]),
                daemon=True
            ).start()
