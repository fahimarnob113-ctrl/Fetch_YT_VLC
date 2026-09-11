import os
import sys
import shutil
import subprocess
import tempfile
from typing import List, Tuple, Optional, Callable
import config


_vlc_cache = None


def find_vlc_path(force_refresh: bool = False) -> Optional[str]:
    """Find VLC executable path with caching and persistent configuration save."""
    global _vlc_cache
    if not force_refresh and _vlc_cache and os.path.isfile(_vlc_cache):
        return _vlc_cache

    # 1. Check user config first
    configured_path = config.get("vlc_path", "")
    if configured_path and os.path.isfile(configured_path):
        _vlc_cache = configured_path
        return configured_path

    # 2. Check system PATH
    for name in ("vlc", "vlc.exe"):
        path = shutil.which(name)
        if path and os.path.isfile(path):
            _vlc_cache = path
            config.set_value("vlc_path", path)
            return path

    # 3. Check OS-specific standard directories
    candidates = []
    if sys.platform.startswith("win"):
        candidates = [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\VideoLAN\VLC\vlc.exe"),
        ]
    elif sys.platform == "darwin":
        candidates = [
            "/Applications/VLC.app/Contents/MacOS/VLC",
            os.path.expanduser("~/Applications/VLC.app/Contents/MacOS/VLC"),
        ]
    else:
        candidates = [
            "/usr/bin/vlc",
            "/usr/local/bin/vlc",
            "/snap/bin/vlc",
            "/var/lib/flatpak/exports/bin/org.videolan.VLC",
        ]

    for c in candidates:
        if os.path.isfile(c):
            _vlc_cache = c
            config.set_value("vlc_path", c)
            return c

    return None


def find_vlc_path_async(callback: Callable[[Optional[str]], None]):
    """Run VLC discovery in a background thread and return path via callback."""
    import threading

    def worker():
        path = find_vlc_path()
        callback(path)

    threading.Thread(target=worker, daemon=True).start()


def get_vlc_version(vlc_path: Optional[str] = None) -> Optional[str]:
    """Attempt to retrieve the installed VLC version."""
    if not vlc_path:
        vlc_path = find_vlc_path()
    if not vlc_path or not os.path.isfile(vlc_path):
        return None

    try:
        creation_flags = 0
        if sys.platform.startswith("win"):
            creation_flags = subprocess.CREATE_NO_WINDOW

        proc = subprocess.run(
            [vlc_path, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3,
            creationflags=creation_flags,
        )
        output = proc.stdout or proc.stderr
        for line in output.splitlines():
            line = line.strip()
            if "VLC media player" in line or "VLC version" in line:
                return line
            elif line.startswith("VLC"):
                return line
        return "Detected"
    except Exception:
        return "Detected"


def _normalize_item(item):
    """Normalize item representation to (title, url, audio_url)."""
    if isinstance(item, dict):
        return item.get("title", "Unknown"), item.get("url", ""), item.get("audio_url")
    elif len(item) == 2:
        return item[0], item[1], None
    elif len(item) >= 3:
        return item[0], item[1], item[2]
    return "Unknown", "", None


def create_m3u_playlist(items: List[Any], file_path: Optional[str] = None) -> str:
    """Create an M3U playlist file supporting separate video and audio tracks via EXTVLCOPT."""
    if file_path is None:
        fd, file_path = tempfile.mkstemp(suffix=".m3u", prefix="yt_vlc_")
        f = os.fdopen(fd, "w", encoding="utf-8")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        f = open(file_path, "w", encoding="utf-8")

    with f:
        f.write("#EXTM3U\n")
        for item in items:
            title, target, audio_url = _normalize_item(item)
            clean_title = title.replace("\n", " ").replace("\r", " ")
            f.write(f"#EXTINF:-1,{clean_title}\n")
            if audio_url:
                f.write(f"#EXTVLCOPT:input-slave={audio_url}\n")
            f.write(f"{target}\n")

    return file_path


def launch_vlc(
    vlc_path: str,
    items: List[Any],
    log_callback: Optional[Callable[[str], None]] = None,
    permanent_m3u_path: Optional[str] = None,
) -> bool:
    """Launch VLC with single item or M3U playlist. Returns True on success."""
    if not items:
        raise RuntimeError("No media items to play.")

    if not vlc_path or not os.path.isfile(vlc_path):
        raise FileNotFoundError(f"VLC executable not found: {vlc_path}")

    log = log_callback or (lambda msg: None)

    if len(items) == 1:
        title, target, audio_url = _normalize_item(items[0])
        log(f"Launching VLC for: {title}")
        cmd = [vlc_path, target]
        if audio_url:
            cmd.append(f":input-slave={audio_url}")
        subprocess.Popen(cmd)
        return True

    # Multiple items: create playlist
    m3u_path = create_m3u_playlist(items, file_path=permanent_m3u_path)
    log(f"Created playlist ({len(items)} items): {m3u_path}")
    log(f"Launching VLC with playlist...")
    subprocess.Popen([vlc_path, m3u_path])
    return True
