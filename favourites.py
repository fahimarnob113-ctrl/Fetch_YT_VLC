import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

FAVOURITES_FILE = Path.home() / ".yt_vlc_favourites.json"


def load_favourites() -> List[Dict[str, Any]]:
    """Load favourites list from JSON file."""
    if not FAVOURITES_FILE.is_file():
        return []
    try:
        with open(FAVOURITES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def save_favourites(entries: List[Dict[str, Any]]) -> bool:
    """Save favourites list to JSON file."""
    try:
        with open(FAVOURITES_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving favourites: {e}")
        return False


def add_favourite(
    title: str,
    source_url: str,
    kind: str = "streamed",
    file_path: Optional[str] = None,
    duration: Optional[str] = None,
) -> Dict[str, Any]:
    """Add or pin a media item to favourites."""
    entries = load_favourites()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if already present
    for i, e in enumerate(entries):
        if e.get("source_url") == source_url:
            # Update title/path if newer and move to top
            e["title"] = title or e.get("title", "Video")
            if file_path:
                e["file_path"] = file_path
                e["kind"] = "downloaded"
            item = entries.pop(i)
            entries.insert(0, item)
            save_favourites(entries)
            return item

    new_item = {
        "title": title or "Favorite Video",
        "source_url": source_url,
        "kind": kind,
        "file_path": file_path,
        "duration": duration or "",
        "added_at": now_str,
    }
    entries.insert(0, new_item)
    save_favourites(entries)
    return new_item


def remove_favourite(index: int) -> bool:
    """Remove item at index from favourites."""
    entries = load_favourites()
    if 0 <= index < len(entries):
        entries.pop(index)
        return save_favourites(entries)
    return False


def move_favourite(from_index: int, to_index: int) -> bool:
    """Move favourite entry to reorder list (e.g., Move Up / Move Down)."""
    entries = load_favourites()
    if 0 <= from_index < len(entries) and 0 <= to_index < len(entries):
        item = entries.pop(from_index)
        entries.insert(to_index, item)
        return save_favourites(entries)
    return False


def clear_favourites() -> bool:
    """Clear all favourites."""
    return save_favourites([])
