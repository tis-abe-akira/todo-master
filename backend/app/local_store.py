import json
import os
import shutil
import tempfile


class LocalStore:
    """Simple local JSON persistence with atomic write and backup support."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.dir = os.path.dirname(os.path.abspath(filepath))
        os.makedirs(self.dir, exist_ok=True)

    def save(self, data):
        """Atomically write JSON data to filepath. Keep a .bak of previous file."""
        # Backup existing file
        if os.path.exists(self.filepath):
            bak_path = self.filepath + ".bak"
            shutil.copy2(self.filepath, bak_path)

        # Write to temporary file in same directory
        fd, tmp_path = tempfile.mkstemp(dir=self.dir)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            # Atomic replace
            os.replace(tmp_path, self.filepath)
        finally:
            # Ensure temp file removed if something failed
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def load(self):
        """Load JSON data. If file is corrupted attempt recovery from .bak."""
        if not os.path.exists(self.filepath):
            return []

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            # Attempt recovery from backup
            bak_path = self.filepath + ".bak"
            if os.path.exists(bak_path):
                # Restore backup
                shutil.copy2(bak_path, self.filepath)
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            # No backup available - propagate error
            raise
