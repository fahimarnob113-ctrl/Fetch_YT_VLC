# YT → VLC Launcher

<p align="center">
  <img src="the%20logo%20or%20icon/app_icon.png" width="130" height="130" alt="YT to VLC Logo" />
  <br>
  <strong>High-Performance YouTube Streaming & Smart Downloads for VLC Media Player</strong>
  <br>
  <em>Stream ad-free in VLC or download at smart, storage-friendly resolutions.</em>
</p>

<p align="center">
  <a href="https://github.com/fahimarnob113-ctrl/Fetch_YT_VLC/releases/download/v3.0.0/YT_VLC.exe">
    <img src="https://img.shields.io/badge/⚡%20Download-YT__VLC.exe%20(v3.0.0)-FF8800?style=for-the-badge&logo=windows&logoColor=white" alt="Download YT_VLC.exe" />
  </a>
  <a href="https://github.com/fahimarnob113-ctrl/Fetch_YT_VLC/releases/tag/v3.0.0">
    <img src="https://img.shields.io/badge/Release-v3.0.0-333333?style=for-the-badge&logo=github" alt="GitHub Release" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Theme-VLC%20Dark-orange?style=flat-square" alt="Theme" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue?style=flat-square" alt="Platform" />
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License" />
</p>

---

## 💡 Why This Exists

VLC's built-in YouTube parser frequently breaks whenever YouTube updates its site algorithms and signature deciphers. 

**YT → VLC Launcher** bridges the gap by using `yt-dlp` to extract clean, high-speed adaptive media streams and hands them straight to VLC with synced video and audio tracks (`:input-slave`). You get the full power of VLC (hardware acceleration, custom audio EQ, hotkeys, playlist queue) with zero browser overhead and zero ads.

---

## ⚡ Quick Download for Windows (No Python Needed)

You don't need Python or command lines to use the app:

1. Click **[Download `YT_VLC.exe` (v3.0.0)](https://github.com/fahimarnob113-ctrl/Fetch_YT_VLC/releases/download/v3.0.0/YT_VLC.exe)** (~37 MB).
2. Double-click `YT_VLC.exe` to launch.
3. Paste any YouTube video or playlist URL and hit **▶ Play in VLC**!

---

## 🌟 Key Features

### 🎬 1. Instant VLC Streaming
- **Adaptive Stream Sync**: Automatically pairs the highest quality video with the optimal audio track via VLC's `:input-slave` engine.
- **Playlist Queueing**: Hands whole playlists over to VLC with auto-generated M3U tracklists.
- **Node.js Decipher Integration**: Automatically uses Node.js (if installed) for fast signature deciphering on restricted formats.

### 📥 2. Smart Storage Downloads
- **Sensible Defaults**: Defaults to **720p** to avoid accidentally pulling massive 4K files that eat gigabytes of disk space.
- **Pre-Download Size Estimation**: Accurately calculates file size *before* starting the download.
- **Large Download Protection**: Warns you if a playlist or file exceeds your warning threshold (configurable, default: 1 GB).
- **Format Flexibility**: Choose between `Auto-best`, `1080p`, `720p`, `480p`, `360p`, or Audio-Only (`MP3` / `M4A`).
- **Real-Time Progress**: Live visual progress bar displaying percent completed, transfer speed, and ETA.

### 🕒 3. Watch History
- Automatically logs all past streams and downloads with titles, dates, and durations.
- **Live Search / Filter**: Filter past videos instantly as you type.
- **Column Sorting**: Sort by timestamp, title, type, or duration with a click.
- **One-Click Replay**: Re-open downloaded files instantly from disk, or re-resolve stream links on the fly.
- **Folder Quick-Jump**: Jump directly to a downloaded file in File Explorer.

### ⭐ 4. Pinned Favourites
- Pin favourite channels, music mixes, or recurring playlists.
- Quick-pin by URL directly or click **⭐ Favourite** in your Watch History.
- Reorder your pinned list with **▲ Move Up** and **▼ Move Down** buttons.

### 📁 5. Persistent Local Playlists
- Save entire YouTube playlists permanently to disk (`~/.yt_vlc_playlists.json`).
- Master-detail split layout allows browsing playlists on the left and tracks on the right.
- **Play All in VLC**: Queues the entire playlist in one click.
- **Play Track**: Double-click any track to stream only that song/video.

### 📦 6. Data Portability (NewPipe-Style Backup)
- **Export Backup (ZIP)**: Exports your complete history, favourites, playlists, and settings into a single `.zip` file.
- **Import Backup (ZIP)**: Restore your setup onto any computer with a single click.

### 🎨 7. Native VLC Dark Theme
- Built using **ttkbootstrap** with a custom dark palette (`#191919`) and iconic VLC orange accents (`#FF8800`).
- High-contrast buttons, responsive layout, and custom traffic-cone play button icon.

---

## ⌨️ Shortcuts Cheatsheet

### 🎧 Inside VLC Player
| Shortcut | Action |
|---|---|
| **`Ctrl + L`** | **Toggle Playlist Queue** (browse all queued videos & click to jump) |
| **`N`** | Next Track / Video |
| **`P`** | Previous Track / Video |
| **`Space`** | Play / Pause |
| **`F`** | Fullscreen Toggle |
| **`Ctrl + Up / Down`** | Volume Up / Down |
| **`M`** | Mute Audio |

### 🖥️ Inside YT → VLC App
| Shortcut | Action |
|---|---|
| **`Enter`** | Start Play / Download in any URL input |
| **`Double-Click`** | Instantly play selected item in History, Favourites, or Playlists |
| **`Ctrl + D`** | Toggle Debug Mode (verbose diagnostics & logs) |

---

## 🛠️ Running from Source Code

If you prefer running or modifying the Python source code:

### Prerequisites
- Python 3.8+
- [VLC Media Player](https://www.videolan.org/vlc/)
- Node.js (recommended for YouTube format extraction)

### Installation
```bash
# Clone the repository
git clone https://github.com/fahimarnob113-ctrl/Fetch_YT_VLC.git
cd Fetch_YT_VLC

# Install Python dependencies
pip install ttkbootstrap yt-dlp

# Launch the app
python main.py
```

### Packaging into `.exe` Yourself
```bash
pip install pyinstaller
python -m PyInstaller --clean yt_vlc.spec
```
The compiled executable will be generated inside the `dist/` directory.

---

## 📂 Architecture Overview

```
Fetch_YT_VLC/
├── main.py              # Application entrypoint & icon hook
├── config.py            # User configuration & persistence (~/.yt_vlc_config.json)
├── theme.py             # Custom VLC Dark theme definition
├── vlc_utils.py         # Path detection, M3U generation, and process launcher
├── ytdlp_utils.py       # Stream resolution, size estimator, and format mapper
├── history.py           # Watch history storage (~/.yt_vlc_history.json)
├── favourites.py        # Pinned favourites storage (~/.yt_vlc_favourites.json)
├── playlists.py         # Persistent local playlists (~/.yt_vlc_playlists.json)
├── export_import.py     # NewPipe-style backup/restore ZIP engine
├── yt_vlc.spec          # PyInstaller standalone build configuration
├── gui/
│   ├── app.py           # Window container, notebook controller, and status bar
│   ├── play_tab.py      # Stream/Download controls, progress bar, log console
│   ├── history_tab.py   # Treeview, live search filter, and replay controls
│   ├── favourites_tab.py# Pinned favourites view and reorder controls
│   ├── playlists_tab.py # Master-detail playlist explorer and shortcuts hint bar
│   └── settings_tab.py  # Preferences, backup export/import, and update check
└── the logo or icon/    # High-resolution 3D renders, vector icons, and Windows ICO
```

---

## ❓ Troubleshooting & FAQ

<details>
<summary><strong>Q: VLC Player is not detected automatically</strong></summary>
<br>
Go to the <strong>Settings</strong> tab (or the Play tab) and click <strong>Browse...</strong> to select your <code>vlc.exe</code> (usually located at <code>C:\Program Files\VideoLAN\VLC\vlc.exe</code> or <code>C:\Program Files (x86)\VideoLAN\VLC\vlc.exe</code>). The app will remember your path permanently.
</details>

<details>
<summary><strong>Q: How do I jump between videos in a playlist while playing?</strong></summary>
<br>
Press <strong><code>Ctrl + L</code></strong> inside VLC to display the live playlist queue. You can double-click any video to switch to it immediately. Alternatively, in the app's <strong>Playlists</strong> tab, double-click any track in the tracklist.
</details>

<details>
<summary><strong>Q: yt-dlp says update available or YouTube changes something</strong></summary>
<br>
Open the <strong>Settings</strong> tab and click <strong>Check for yt-dlp Updates</strong>. If an update is detected, the app will update yt-dlp for you in the background with a single click.
</details>

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
