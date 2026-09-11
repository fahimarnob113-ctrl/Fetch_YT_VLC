import os
import json
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, Any

from history import HISTORY_FILE
from favourites import FAVOURITES_FILE
from playlists import PLAYLISTS_FILE
from config import CONFIG_FILE

DATA_FILES = {
    "history.json": HISTORY_FILE,
    "favourites.json": FAVOURITES_FILE,
    "playlists.json": PLAYLISTS_FILE,
    "config.json": CONFIG_FILE,
}


def export_backup(dest_zip_path: str) -> Tuple[bool, str]:
    """Export all user data, history, playlists, and settings to a NewPipe-style ZIP archive."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(dest_zip_path)), exist_ok=True)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        metadata = {
            "app": "YT to VLC Launcher",
            "version": "3.0",
            "created_at": now_str,
            "included_files": [],
        }

        with zipfile.ZipFile(dest_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for arch_name, file_path in DATA_FILES.items():
                if file_path.is_file():
                    zf.write(file_path, arcname=arch_name)
                    metadata["included_files"].append(arch_name)
                else:
                    # Create empty placeholder if not created yet
                    zf.writestr(arch_name, "[]" if "config" not in arch_name else "{}")
                    metadata["included_files"].append(arch_name)

            zf.writestr("backup_info.json", json.dumps(metadata, indent=2))

        return True, f"Backup successfully exported with {len(metadata['included_files'])} data files."
    except Exception as e:
        return False, f"Failed to create backup: {e}"


def import_backup(src_zip_path: str) -> Tuple[bool, str, Dict[str, Any]]:
    """Import and restore all data files from a previously exported ZIP archive."""
    stats = {"restored": [], "errors": []}
    if not os.path.isfile(src_zip_path):
        return False, "Selected backup file does not exist.", stats

    try:
        with zipfile.ZipFile(src_zip_path, "r") as zf:
            file_list = zf.namelist()
            for arch_name, dest_file in DATA_FILES.items():
                if arch_name in file_list:
                    content = zf.read(arch_name)
                    # Validate JSON structure before writing
                    try:
                        json.loads(content.decode("utf-8"))
                        with open(dest_file, "wb") as f:
                            f.write(content)
                        stats["restored"].append(arch_name)
                    except Exception as json_err:
                        stats["errors"].append(f"{arch_name}: Invalid JSON ({json_err})")

            # Reload memory caches
            import config
            config.load_config()

        if stats["restored"]:
            return True, f"Successfully restored: {', '.join(stats['restored'])}", stats
        else:
            return False, "No valid data files were found inside this backup archive.", stats

    except Exception as e:
        return False, f"Failed to restore backup: {e}", stats
