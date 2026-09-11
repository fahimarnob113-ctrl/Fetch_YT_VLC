import os
import sys
import json
import urllib.request
import subprocess
import shutil
from typing import List, Tuple, Optional, Callable, Dict, Any
import config

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

FORMAT_MAP = {
    "Auto-best": "bestvideo*+bestaudio/best",
    "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
    "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
    "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
    "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]/best",
    "Audio only (MP3)": "bestaudio/best",
    "Audio only (M4A)": "bestaudio[ext=m4a]/bestaudio/best",
}


def is_ytdlp_available() -> bool:
    return yt_dlp is not None


def format_duration(seconds: Optional[int]) -> str:
    if not seconds:
        return ""
    try:
        s = int(seconds)
        h = s // 3600
        m = (s % 3600) // 60
        sec = s % 60
        if h > 0:
            return f"{h}:{m:02d}:{sec:02d}"
        return f"{m}:{sec:02d}"
    except Exception:
        return ""


def validate_url(url: str) -> Tuple[bool, str]:
    """Validate user input URL. Returns (is_valid, error_message)."""
    u = url.strip()
    if not u:
        return False, "URL is empty. Please paste a video or playlist link."
    if not (u.startswith("http://") or u.startswith("https://")):
        return False, "Invalid URL: Must start with http:// or https://"
    return True, ""


def get_version_info() -> Dict[str, Any]:
    """Check installed yt-dlp version against latest version published on PyPI."""
    installed_ver = None
    if yt_dlp:
        try:
            from yt_dlp.version import __version__ as ytdlp_ver
            installed_ver = ytdlp_ver
        except Exception:
            installed_ver = getattr(yt_dlp, "__version__", None)

    result = {
        "installed": installed_ver or "Not Installed",
        "latest": None,
        "update_available": False,
    }

    try:
        req = urllib.request.Request(
            "https://pypi.org/pypi/yt-dlp/json",
            headers={"User-Agent": "YT-VLC-Launcher/3.0"}
        )
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            latest_ver = data.get("info", {}).get("version")
            result["latest"] = latest_ver
            if installed_ver and latest_ver:
                try:
                    def parse_v(v_str):
                        return tuple(int(p) for p in v_str.replace("-", ".").split(".") if p.isdigit())
                    result["update_available"] = parse_v(latest_ver) > parse_v(installed_ver)
                except Exception:
                    result["update_available"] = installed_ver != latest_ver
    except Exception:
        pass

    return result


def update_ytdlp(log_callback: Optional[Callable[[str], None]] = None) -> bool:
    """Run pip to update yt-dlp to latest version."""
    log = log_callback or (lambda msg: None)
    log("Checking and updating yt-dlp via pip...")
    try:
        creation_flags = 0
        if sys.platform.startswith("win"):
            creation_flags = subprocess.CREATE_NO_WINDOW

        proc = subprocess.Popen(
            [sys.executable, "-m", "pip", "install", "-U", "yt-dlp"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=creation_flags,
        )
        for line in proc.stdout:
            log(line.strip())
        proc.wait()
        if proc.returncode == 0:
            log("yt-dlp update successful! Please restart the app if needed.")
            return True
        else:
            log(f"yt-dlp update exited with code {proc.returncode}")
            return False
    except Exception as e:
        log(f"Failed to update yt-dlp: {e}")
        return False


def resolve_urls(
    input_url: str,
    quality: str = "720p",
    log_callback: Optional[Callable[[str], None]] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Resolves stream URLs for single video or playlist without downloading.
    Returns: (list_of_entries, metadata_dict)
    where each entry has:
      {"title": str, "url": str, "duration": str, "thumbnail": str, "uploader": str}
    """
    if not is_ytdlp_available():
        raise RuntimeError("yt-dlp is not installed. Run: pip install yt-dlp")

    log = log_callback or (lambda msg: None)
    fmt = FORMAT_MAP.get(quality, FORMAT_MAP["720p"])

    is_debug = config.get("debug_mode", False)
    ydl_opts = {
        "quiet": not is_debug,
        "no_warnings": not is_debug,
        "format": fmt,
        "noplaylist": False,
        "extract_flat": False,
    }

    # Enable Node.js runtime if available to avoid JS-runtime warnings and unlock all formats
    if shutil.which("node"):
        ydl_opts["js_runtimes"] = {"node": {}}

    log(f"Resolving: {input_url} (Format: {quality})")
    results = []
    meta = {}

    def extract_entry_urls(entry_dict):
        """Extract video stream url and optional audio stream url from yt-dlp entry."""
        s_url = None
        a_url = None
        reqs = entry_dict.get("requested_formats")
        if reqs:
            # Look for video format and separate audio format
            v_fmt = next((f for f in reqs if f.get("vcodec") not in (None, "none")), reqs[0])
            a_fmt = next((f for f in reqs if f.get("acodec") not in (None, "none") and f != v_fmt), None)
            s_url = v_fmt.get("url")
            if a_fmt:
                a_url = a_fmt.get("url")
        elif entry_dict.get("url"):
            s_url = entry_dict.get("url")
        elif entry_dict.get("formats"):
            # Fallback to the last format in the list
            for f in reversed(entry_dict["formats"]):
                if f.get("url"):
                    s_url = f.get("url")
                    break
        return s_url, a_url

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(input_url, download=False)
        if not info:
            raise RuntimeError("yt-dlp could not extract any information from this URL.")

        meta["title"] = info.get("title", "Unknown")
        meta["uploader"] = info.get("uploader", "")
        meta["thumbnail"] = info.get("thumbnail", "")
        meta["is_playlist"] = "entries" in info

        if "entries" in info:
            raw_entries = [e for e in info["entries"] if e]
            log(f"Found playlist with {len(raw_entries)} videos")
            meta["playlist_title"] = info.get("title", "Playlist")
            meta["count"] = len(raw_entries)

            for idx, entry in enumerate(raw_entries, 1):
                stream_url, audio_url = extract_entry_urls(entry)
                title = entry.get("title", f"Track {idx}")
                dur = format_duration(entry.get("duration"))
                thumb = entry.get("thumbnail", "")
                uploader = entry.get("uploader", "")

                if stream_url:
                    results.append({
                        "title": title,
                        "url": stream_url,
                        "audio_url": audio_url,
                        "duration": dur,
                        "thumbnail": thumb,
                        "uploader": uploader,
                        "index": idx,
                    })
                else:
                    log(f"  [Skipping] Stream URL missing for item #{idx}: {title}")
        else:
            title = info.get("title", "Unknown Video")
            stream_url, audio_url = extract_entry_urls(info)
            dur = format_duration(info.get("duration"))
            thumb = info.get("thumbnail", "")
            uploader = info.get("uploader", "")

            if stream_url:
                results.append({
                    "title": title,
                    "url": stream_url,
                    "audio_url": audio_url,
                    "duration": dur,
                    "thumbnail": thumb,
                    "uploader": uploader,
                    "index": 1,
                })

    if not results:
        raise RuntimeError("No playable stream URLs found for this URL.")

    return results, meta


def estimate_size(
    input_url: str,
    quality: str = "720p",
    log_callback: Optional[Callable[[str], None]] = None,
) -> Tuple[int, bool]:
    """
    Estimates total download size in bytes.
    Returns: (total_bytes, is_approximate)
    """
    if not is_ytdlp_available():
        return 0, True

    fmt = FORMAT_MAP.get(quality, FORMAT_MAP["720p"])
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": fmt,
        "simulate": True,
    }
    if shutil.which("node"):
        ydl_opts["js_runtimes"] = {"node": {}}

    total_bytes = 0
    approximate = False

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(input_url, download=False)
            entries = info["entries"] if "entries" in info else [info]
            for entry in entries:
                if not entry:
                    continue
                size = entry.get("filesize") or entry.get("filesize_approx")
                if size:
                    total_bytes += size
                else:
                    # Rough estimate based on duration (approx 4 MB per minute for 720p)
                    dur = entry.get("duration", 0)
                    if dur:
                        total_bytes += int(dur * (4 * 1024 * 1024 / 60))
                        approximate = True
                    else:
                        approximate = True
    except Exception:
        approximate = True

    return total_bytes, approximate


def download_locally(
    input_url: str,
    download_dir: str,
    quality: str = "720p",
    progress_hook: Optional[Callable[[Dict[str, Any]], None]] = None,
    log_callback: Optional[Callable[[str], None]] = None,
    cancel_check: Optional[Callable[[], bool]] = None,
) -> List[Tuple[str, str]]:
    """
    Downloads media locally with format selection and progress hooks.
    Returns: list of (title, local_file_path)
    """
    if not is_ytdlp_available():
        raise RuntimeError("yt-dlp is not installed. Run: pip install yt-dlp")

    log = log_callback or (lambda msg: None)
    os.makedirs(download_dir, exist_ok=True)
    downloaded = []

    def internal_hook(d):
        if cancel_check and cancel_check():
            raise RuntimeError("Download cancelled by user.")
        if progress_hook:
            progress_hook(d)
        if d.get("status") == "finished":
            fname = os.path.basename(d.get("filename", ""))
            log(f"  Finished file: {fname}")

    fmt = FORMAT_MAP.get(quality, FORMAT_MAP["720p"])
    is_audio = "Audio only" in quality

    ydl_opts = {
        "quiet": not config.get("debug_mode", False),
        "no_warnings": not config.get("debug_mode", False),
        "format": fmt,
        "outtmpl": os.path.join(
            download_dir,
            "%(playlist_title|)s%(playlist_index& - |)s%(title)s.%(ext)s"
        ),
        "progress_hooks": [internal_hook],
        "noplaylist": False,
    }
    if shutil.which("node"):
        ydl_opts["js_runtimes"] = {"node": {}}

    if is_audio:
        if "MP3" in quality:
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        elif "M4A" in quality:
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }]

    log(f"Downloading to: {download_dir} (Quality: {quality})")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(input_url, download=True)
        entries = info["entries"] if "entries" in info else [info]
        for entry in entries:
            if not entry:
                continue
            title = entry.get("title", "Unknown")
            try:
                filepath = ydl.prepare_filename(entry)
                # If audio postprocessing was applied, extension might change to .mp3/.m4a
                if is_audio:
                    base, _ = os.path.splitext(filepath)
                    if "MP3" in quality and os.path.isfile(base + ".mp3"):
                        filepath = base + ".mp3"
                    elif "M4A" in quality and os.path.isfile(base + ".m4a"):
                        filepath = base + ".m4a"
            except Exception:
                filepath = None

            if filepath and os.path.isfile(filepath):
                downloaded.append((title, filepath))
            else:
                log(f"  Warning: couldn't locate confirmed file on disk for: {title}")

    return downloaded
