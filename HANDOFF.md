# Project Handoff: YT → VLC Launcher

## What this is

A standalone desktop GUI app (Python + tkinter) that lets a user paste a
YouTube video or playlist URL and either:
1. **Stream it directly into VLC** (no files saved), or
2. **Download it locally** for offline viewing

It also keeps a **watch history** log so past videos can be replayed or
located on disk later.

This exists because VLC's built-in YouTube support is unreliable (breaks
whenever YouTube changes its site). The app uses `yt-dlp` — a
actively-maintained library — to resolve/download the actual media, then
hands that off to VLC.

## Current state: functional, untested against live YouTube

The code is written and syntax-verified (`py_compile` passes), but **has
not been run against a real YouTube URL** — the sandbox this was built in
has no network access. Before relying on it, run it locally end-to-end
with a real video and a real playlist.

## Files delivered

| File | Purpose |
|---|---|
| `yt_vlc_app_v2.py` | **Current/main app.** Two-tab GUI: Play/Download + History. |
| `yt_vlc_app.py` | Earlier version — streaming only, no download or history. Kept for reference; not needed if using v2. |
| `README.md` | End-user setup and usage instructions. |

## Requirements to run

- Python 3.8+
- `pip install yt-dlp`
- VLC installed locally (app auto-detects common install paths on
  Windows/Mac/Linux, or can be pointed at manually via "Browse")

Run with:
```
python3 yt_vlc_app_v2.py
```

## Architecture / how it works

- **`find_vlc_path()`** — checks `PATH`, then common per-OS install
  locations, for the VLC binary.
- **`resolve_urls()`** — uses `yt_dlp.YoutubeDL.extract_info(download=False)`
  to get direct stream URL(s) without downloading. Handles both single
  videos and playlists (checks for an `entries` key).
- **`download_locally()`** — same extraction, but `download=True`, saving
  files to a user-chosen folder. Playlist items are named with the
  playlist title + index prefix to preserve order.
- **`launch_vlc()`** — a single item is passed straight to VLC as an
  argument; multiple items are written to a temporary `.m3u` playlist
  file, which VLC opens as a queue.
- **History** — a flat JSON file at `~/.yt_vlc_history.json`, capped at
  500 entries, storing title, source URL, timestamp, type
  (`streamed`/`downloaded`), and local file path (if downloaded).
  Streamed entries are re-resolved on replay since raw stream URLs
  expire; downloaded entries just reopen the saved file.
- **GUI** — plain `tkinter`, no extra UI dependencies. Long-running
  yt-dlp calls run in a background `threading.Thread` so the window
  doesn't freeze.

## Known limitations / things to check next

- **Not yet tested live.** Test with: a single public video, a full
  playlist, and a private/age-restricted video (expected to fail without
  extra auth — see below).
- **Age-restricted / private / members-only videos** will likely fail to
  resolve. yt-dlp supports passing cookies for authenticated access; not
  implemented yet.
- **yt-dlp goes stale.** It needs periodic updates (`pip install -U
  yt-dlp`) as YouTube changes its site. Consider adding an in-app
  "check for yt-dlp update" button if this app gets real usage.
- **No packaged executable yet.** Currently requires Python + pip
  installs. README documents a PyInstaller path
  (`pyinstaller --onefile --windowed yt_vlc_app_v2.py`) to produce a
  double-clickable `.exe`/`.app`, but that hasn't been built or tested.
- **Format selection is fixed to `"best"`.** No UI control yet for
  choosing resolution/quality or audio-only downloads.
- **No progress bar in the GUI** — download progress is only visible as
  text in the log pane, not a visual bar.

## Possible next steps

- Add cookie-based auth support for private/members content.
- Add a quality/format picker (e.g. 1080p vs audio-only).
- Add a "Update yt-dlp" button in the GUI.
- Package with PyInstaller and test the resulting binary on a clean
  machine (one without Python installed).
- Add a visual progress bar for downloads instead of log-only output.
