# YT → VLC Launcher (v3)

<p align="center">
  <img src="the%20logo%20or%20icon/app_icon.png" width="140" height="140" alt="YT to VLC Logo" />
  <br>
  <strong>Direct YouTube Streaming & Smart Downloads for VLC Media Player</strong>
</p>

<p align="center">
  <a href="https://github.com/fahimarnob113-ctrl/Fetch_YT_VLC/releases/latest">
    <img src="https://img.shields.io/badge/Download-YT__VLC.exe%20(v3.0.0)-FF8800?style=for-the-badge&logo=windows&logoColor=white" alt="Download Standalone EXE" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Theme-VLC%20Dark-orange" alt="Theme" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue" alt="Platform" />
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License" />
</p>

---

A fast, standalone desktop application built with Python and **ttkbootstrap** that lets you stream YouTube videos and playlists directly into **VLC Media Player** without ads or browser overhead, or download them locally at smart, storage-efficient resolutions.

---

## ⚡ Quick Download (No Python Needed!)

If you just want to run the app without installing Python or running commands:

👉 **[Download the latest `YT_VLC.exe` from Releases](https://github.com/fahimarnob113-ctrl/Fetch_YT_VLC/releases/latest)**

1. Download **`YT_VLC.exe`**.
2. Double-click to run — no setup or dependencies required!

---

## ✨ Features

- **Direct VLC Streaming**: Stream any video or playlist directly into VLC with synced video and audio streams (`:input-slave` adaptive stream support).
- **Smart Sizing & Downloads**:
  - Choose resolutions from 360p up to 1080p, or Audio-Only (MP3 / M4A).
  - Defaults to **720p** to conserve bandwidth and disk space.
  - Automatically estimates file size before downloading.
  - Size warning protection before starting large downloads.
  - Real-time progress bar displaying percent, download speed, and ETA.
- **Watch History**:
  - Tracks all streamed and downloaded media with timestamps, titles, and durations.
  - Instant live search/filtering as you type.
  - Sort by column headers (When, Title, Type, Duration).
  - Double-click or press *Play Selected* to replay instantly.
  - Open containing folder directly for downloaded files.
- **Pinned Favourites**:
  - Pin favourite tracks or playlists directly by URL or from watch history.
  - Reorder items with Move Up / Move Down buttons.
- **Persistent Playlists**:
  - Fetch and store complete YouTube playlists permanently on your machine (`~/.yt_vlc_playlists.json`).
  - Master-detail split view with track listing.
  - One-click *Play All in VLC* to queue up the full playlist.
- **Data Portability (NewPipe Style)**:
  - Export your entire app data (History, Playlists, Favourites, Preferences) into a single `.zip` backup.
  - Restore on any computer with one click.
- **Modern VLC Dark Theme**: Custom dark theme with iconic VLC orange accents and high-contrast, responsive controls.
- **Node.js Integration**: Automatically detects Node.js for decoding modern YouTube signatures and extracting full-format streams.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Where | Action |
|---|---|---|
| **`Ctrl + L`** | In VLC | **Show / Hide Playlist Queue** (see all videos & click to jump) |
| **`Space`** | In VLC | Play / Pause |
| **`N` / `P`** | In VLC | Next / Previous video in playlist |
| **`F`** | In VLC | Toggle Fullscreen |
| **`Ctrl + D`** | In App | Toggle Debug Mode (verbose diagnostics) |
| **`Enter`** | In App | Run Play / Go in URL entry fields |
| **`Double-Click`** | In App | Instantly play selected video in History, Favourites, or Playlists |

---

## 🚀 Running from Source

### Requirements
- **Python 3.8+**
- **VLC Media Player** installed on your system ([Download VLC](https://www.videolan.org/vlc/))
- **Node.js** (recommended for YouTube format extraction)

### Installation
```bash
git clone https://github.com/fahimarnob113-ctrl/Fetch_YT_VLC.git
cd Fetch_YT_VLC
pip install ttkbootstrap yt-dlp
python main.py
```

---

## 🛠️ Project Structure
```
Fetch_YT_VLC/
├── main.py              # Application entry point
├── config.py            # Configuration loader and persistence
├── theme.py             # Custom VLC Dark theme definition
├── vlc_utils.py         # VLC discovery, M3U generation, and process launcher
├── ytdlp_utils.py       # Stream resolution, size estimation, and download hooks
├── history.py           # Watch history storage and search operations
├── favourites.py        # Pinned favourites storage
├── playlists.py         # Persistent local playlist storage
├── export_import.py     # NewPipe-style backup/restore ZIP archive
├── yt_vlc.spec          # PyInstaller build specification
├── gui/
│   ├── app.py           # Main window shell, notebook tabs, and status bar
│   ├── play_tab.py      # Play & Download controls, progress bar, activity log
│   ├── history_tab.py   # Watch history list, search filter, and replay controls
│   ├── favourites_tab.py# Pinned favourites management
│   ├── playlists_tab.py # Persistent local playlists view
│   └── settings_tab.py  # Preferences, backup/restore, and updates
├── the logo or icon/    # High-res logos, minimal vectors, and Windows ICO files
└── YT_Prev/             # Legacy v2 prototypes and reference documents
```

---

## 📄 License
MIT License
