# YT → VLC Launcher (v3)

A fast, standalone desktop application built with Python and **ttkbootstrap** that lets you stream YouTube videos and playlists directly into **VLC Media Player** without ads or browser overhead, or download them locally at smart, storage-efficient resolutions.

![VLC Theme](https://img.shields.io/badge/Theme-VLC%20Dark-orange)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

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
- **Modern VLC Dark Theme**: Custom dark theme with iconic VLC orange accents and high-contrast, responsive controls.
- **Node.js Integration**: Automatically detects Node.js for decoding modern YouTube signatures and extracting full-format streams.

---

## 🚀 Getting Started

### 1. Requirements
- **Python 3.8+**
- **VLC Media Player** installed on your system ([Download VLC](https://www.videolan.org/vlc/))
- **Node.js** (recommended for YouTube format extraction)

### 2. Installation
Clone the repository and install required packages:
```bash
git clone https://github.com/fahimarnob113-ctrl/Fetch_YT_VLC.git
cd Fetch_YT_VLC
pip install ttkbootstrap yt-dlp
```

### 3. Run the App
```bash
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
├── gui/
│   ├── app.py           # Main window shell, notebook tabs, and status bar
│   ├── play_tab.py      # Play & Download controls, progress bar, activity log
│   └── history_tab.py   # Watch history list, search filter, and replay controls
└── YT_Prev/             # Legacy v2 prototypes and reference documents
```

---

## 📄 License
MIT License
