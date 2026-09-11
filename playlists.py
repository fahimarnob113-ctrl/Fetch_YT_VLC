import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

PLAYLISTS_FILE = Path.home() / ".yt_vlc_playlists.json"


def load_playlists() -> List[Dict[str, Any]]:
    """Load persistent playlists from JSON file."""
    if not PLAYLISTS_FILE.is_file():
        return []
    try:
        with open(PLAYLISTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def save_playlists(playlists: List[Dict[str, Any]]) -> bool:
    """Save playlists to JSON file."""
    try:
        with open(PLAYLISTS_FILE, "w", encoding="utf-8") as f:
            json.dump(playlists, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving playlists: {e}")
        return False


def create_playlist(name: str, source_url: str = "", items: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Create and persist a new playlist."""
    playlists = load_playlists()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pl_id = f"pl_{int(time.time() * 1000)}"

    clean_items = []
    if items:
        for idx, it in enumerate(items, 1):
            clean_items.append({
                "title": it.get("title", f"Track {idx}"),
                "url": it.get("url", ""),
                "audio_url": it.get("audio_url"),
                "duration": it.get("duration", ""),
                "thumbnail": it.get("thumbnail", ""),
                "index": idx,
            })

    # Check if a playlist with same source_url already exists
    if source_url:
        for p in playlists:
            if p.get("source_url") == source_url:
                p["name"] = name or p.get("name", "Playlist")
                if clean_items:
                    p["items"] = clean_items
                save_playlists(playlists)
                return p

    new_pl = {
        "id": pl_id,
        "name": name or f"Playlist {len(playlists) + 1}",
        "source_url": source_url,
        "created_at": now_str,
        "items": clean_items,
    }
    playlists.insert(0, new_pl)
    save_playlists(playlists)
    return new_pl


def get_playlist(playlist_id: str) -> Optional[Dict[str, Any]]:
    """Get a playlist by its ID."""
    for p in load_playlists():
        if p.get("id") == playlist_id:
            return p
    return None


def delete_playlist(playlist_id: str) -> bool:
    """Delete playlist by ID."""
    playlists = load_playlists()
    initial_len = len(playlists)
    playlists = [p for p in playlists if p.get("id") != playlist_id]
    if len(playlists) < initial_len:
        return save_playlists(playlists)
    return False


def rename_playlist(playlist_id: str, new_name: str) -> bool:
    """Rename an existing playlist."""
    playlists = load_playlists()
    for p in playlists:
        if p.get("id") == playlist_id:
            p["name"] = new_name.strip()
            return save_playlists(playlists)
    return False


def add_item_to_playlist(playlist_id: str, item: Dict[str, Any]) -> bool:
    """Append a single track to an existing playlist."""
    playlists = load_playlists()
    for p in playlists:
        if p.get("id") == playlist_id:
            items = p.setdefault("items", [])
            idx = len(items) + 1
            items.append({
                "title": item.get("title", f"Track {idx}"),
                "url": item.get("url", ""),
                "audio_url": item.get("audio_url"),
                "duration": item.get("duration", ""),
                "thumbnail": item.get("thumbnail", ""),
                "index": idx,
            })
            return save_playlists(playlists)
    return False


def remove_item_from_playlist(playlist_id: str, item_index: int) -> bool:
    """Remove a track at index from a playlist."""
    playlists = load_playlists()
    for p in playlists:
        if p.get("id") == playlist_id:
            items = p.get("items", [])
            if 0 <= item_index < len(items):
                items.pop(item_index)
                # Re-index
                for i, it in enumerate(items, 1):
                    it["index"] = i
                return save_playlists(playlists)
    return False
