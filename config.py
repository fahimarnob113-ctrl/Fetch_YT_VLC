import os
import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".yt_vlc_config.json"

DEFAULT_CONFIG = {
    "vlc_path": "",
    "download_dir": str(Path.home() / "Videos" / "YT-VLC-Downloads"),
    "default_mode": "stream",
    "default_quality": "720p",
    "paste_and_go": False,
    "auto_open_vlc": True,
    "warn_size_threshold_mb": 1024,
    "history_cap": 500,
    "auto_clean_history": False,
    "auto_clean_days": 30,
    "debug_mode": False,
    "theme": "vlc_dark",
}

_cached_config = None


def load_config():
    """Load configuration from disk, falling back to defaults for missing keys."""
    global _cached_config
    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_FILE.is_file():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    cfg.update(saved)
        except Exception:
            pass
    _cached_config = cfg
    return cfg


def save_config(cfg=None):
    """Save current configuration to disk."""
    global _cached_config
    if cfg is None:
        cfg = _cached_config or DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        _cached_config = cfg
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def get(key, default=None):
    """Get a configuration value."""
    global _cached_config
    if _cached_config is None:
        load_config()
    return _cached_config.get(key, default if default is not None else DEFAULT_CONFIG.get(key))


def set_value(key, value):
    """Set and persist a configuration key/value pair."""
    global _cached_config
    if _cached_config is None:
        load_config()
    _cached_config[key] = value
    save_config(_cached_config)
