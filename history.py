import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import config

HISTORY_FILE = Path.home() / ".yt_vlc_history.json"


def load_history() -> List[Dict[str, Any]]:
    """Load history from JSON file."""
    if not HISTORY_FILE.is_file():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def save_history(entries: List[Dict[str, Any]]) -> bool:
    """Save history entries to JSON file."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving history: {e}")
        return False


def add_entry(
    title: str,
    source_url: str,
    kind: str,  # 'streamed' or 'downloaded'
    file_path: Optional[str] = None,
    duration: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a new history entry at the front of the history list."""
    entries = load_history()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = {
        "title": title or "Unknown",
        "source_url": source_url,
        "kind": kind,
        "file_path": file_path,
        "duration": duration or "",
        "timestamp": now_str,
    }

    # Avoid immediate exact duplicates at the very top
    if entries and entries[0].get("source_url") == source_url and entries[0].get("kind") == kind:
        entries[0] = entry
    else:
        entries.insert(0, entry)

    # Trim to config capacity
    cap = config.get("history_cap", 500)
    entries = entries[:cap]

    # Optional auto-clean
    if config.get("auto_clean_history", False):
        days = config.get("auto_clean_days", 30)
        cutoff = datetime.now() - timedelta(days=days)
        filtered = []
        for e in entries:
            try:
                e_time = datetime.strptime(e.get("timestamp", ""), "%Y-%m-%d %H:%M:%S")
                if e_time >= cutoff or e.get("kind") == "downloaded":
                    filtered.append(e)
            except Exception:
                filtered.append(e)
        entries = filtered

    save_history(entries)
    return entry


def delete_entry(index: int) -> bool:
    """Delete entry at specific index."""
    entries = load_history()
    if 0 <= index < len(entries):
        entries.pop(index)
        return save_history(entries)
    return False


def clear_history() -> bool:
    """Clear all history entries."""
    return save_history([])


def search_history(query: str) -> List[Dict[str, Any]]:
    """Filter history by title or source URL."""
    entries = load_history()
    if not query:
        return entries
    q = query.lower()
    return [e for e in entries if q in e.get("title", "").lower() or q in e.get("source_url", "").lower()]
