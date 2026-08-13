import os
import shutil
import time
import win32file
import win32con
import pywintypes

class FileLocker:
    def __init__(self, quarantine_dir):
        self.quarantine_dir = quarantine_dir
        os.makedirs(self.quarantine_dir, exist_ok=True)
        self._active_handles = {}

    def lock_file(self, filepath):
        """Applies exclusive lock (FILE_SHARE_NONE) so no other application can open or execute the file."""
        if not os.path.exists(filepath):
            return False, None

        try:
            # Open file with dwShareMode = 0 (FILE_SHARE_NONE)
            handle = win32file.CreateFile(
                filepath,
                win32con.GENERIC_READ | win32con.GENERIC_WRITE,
                0,  # Exclusive lock - NO sharing
                None,
                win32con.OPEN_EXISTING,
                win32con.FILE_ATTRIBUTE_NORMAL,
                None
            )
            self._active_handles[filepath] = handle
            return True, handle
        except pywintypes.error as e:
            # Handle may fail if file is currently open or downloading
            return False, None

    def unlock_file(self, filepath):
        """Releases the exclusive lock handle, allowing normal system access."""
        if filepath in self._active_handles:
            try:
                win32file.CloseHandle(self._active_handles[filepath])
            except Exception:
                pass
            del self._active_handles[filepath]
            return True
        return False

    def quarantine_file(self, filepath, threat_info="Malicious Payload"):
        """Unlocks and moves malicious file into isolated Quarantine vault."""
        self.unlock_file(filepath)
        if not os.path.exists(filepath):
            return None

        timestamp = int(time.time())
        filename = os.path.basename(filepath)
        quarantined_name = f"{timestamp}_{filename}.quarantine"
        target_path = os.path.join(self.quarantine_dir, quarantined_name)

        try:
            shutil.move(filepath, target_path)
            meta_path = target_path + ".json"
            with open(meta_path, "w") as f:
                import json
                json.dump({
                    "original_path": filepath,
                    "quarantine_time": timestamp,
                    "threat": threat_info
                }, f, indent=2)
            return target_path
        except Exception as e:
            print(f"[FileLocker] Quarantine error: {e}")
            return None
