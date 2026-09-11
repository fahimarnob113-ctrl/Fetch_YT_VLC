# YT → VLC Launcher

A small standalone GUI app: paste a YouTube video or playlist URL, and either
stream it straight into VLC, or download it to disk for offline viewing —
plus a watch history tab so you can revisit or replay anything later.

Use `yt_vlc_app_v2.py` — it has two tabs:

- **Play / Download** — paste a URL, choose "Stream now" or "Download for
  offline viewing" (pick a save folder), then hit Go.
- **History** — every video you've streamed or downloaded is logged here
  with title, date, and type. Select an entry and click "Play selected" to
  reopen it in VLC (downloaded files play instantly from disk; streamed
  entries get their stream link re-resolved, since those links expire).
  "Open containing folder" jumps to a downloaded file on disk. History is
  stored locally in `~/.yt_vlc_history.json`.

## Setup

1. **Python 3.8+** — should already be on most systems. Check with:
   ```
   python3 --version
   ```

2. **Install yt-dlp**:
   ```
   pip install yt-dlp
   ```

3. **Install VLC** if you don't have it: https://www.videolan.org/vlc/

4. **Run the app**:
   ```
   python3 yt_vlc_app_v2.py
   ```
   (On Windows, `python yt_vlc_app_v2.py`)

The app will try to auto-detect your VLC install. If it can't find it,
use the "Browse..." button to point it at the VLC executable directly
(e.g. `C:\Program Files\VideoLAN\VLC\vlc.exe` or
`/Applications/VLC.app/Contents/MacOS/VLC`).

## How it works

- **Single video**: yt-dlp resolves the direct media URL, and VLC is
  launched with that URL directly.
- **Playlist**: yt-dlp extracts every video in the playlist, and the app
  builds a temporary `.m3u` playlist file that VLC opens as a queue —
  this is more reliable than VLC's built-in (and often broken) native
  YouTube playlist parsing.

## Turning this into a "real" double-clickable app (optional)

The script above requires Python to be installed. If you want a single
`.exe` (Windows) or `.app` (Mac) that doesn't require the user to have
Python, package it with **PyInstaller**:

```
pip install pyinstaller
pyinstaller --onefile --windowed yt_vlc_app_v2.py
```

This produces a standalone executable in the `dist/` folder. Note that
`yt-dlp` still needs to be bundled or installed — PyInstaller will
include it automatically since it's imported directly in the script.

## Notes / limitations

- This relies on yt-dlp staying up to date with YouTube's site changes.
  If playback stops working, run `pip install -U yt-dlp` to update it.
- Very large playlists may take a little while to resolve since yt-dlp
  fetches metadata for each video before building the `.m3u`.
- Age-restricted or private videos may fail to resolve without
  additional yt-dlp authentication options (e.g. cookies) — ask if you
  want that added.
- Downloaded files default to `~/Videos/YT-VLC-Downloads/` (changeable
  in the app). Playlist downloads are prefixed with the playlist name
  and index so they stay in order in your file browser.
- Watch history is a plain JSON file (`~/.yt_vlc_history.json`) capped
  at the 500 most recent entries — easy to inspect, back up, or wipe.
