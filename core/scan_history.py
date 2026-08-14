import os
import json
import time
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "scan_history.json"))

class ScanHistoryManager:
    """Thread-safe scan history tracker for all downloads."""

    def __init__(self, max_entries=200):
        self.max_entries = max_entries
        self.lock = threading.Lock()
        self.scanned_count = 0
        self.history = []
        self._load_history()

    def _load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.history = data.get("history", [])
                    self.scanned_count = data.get("scanned_count", len(self.history))
            except Exception as e:
                print(f"[ScanHistoryManager] Error loading history: {e}")

    def _save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "scanned_count": self.scanned_count,
                    "history": self.history
                }, f, indent=2)
        except Exception as e:
            print(f"[ScanHistoryManager] Error saving history: {e}")

    def record_scan(self, filepath, status, finding):
        with self.lock:
            self._load_history()
            self.scanned_count += 1
            entry = {
                "id": self.scanned_count,
                "filename": os.path.basename(filepath),
                "filepath": filepath,
                "status": status,  # "SAFE" or "QUARANTINED"
                "finding": finding,
                "timestamp": int(time.time())
            }
            self.history.insert(0, entry)
            if len(self.history) > self.max_entries:
                self.history = self.history[:self.max_entries]
            self._save_history()

    def get_stats(self):
        with self.lock:
            self._load_history()
            return {
                "scanned_count": max(self.scanned_count, len(self.history)),
                "history": list(self.history)
            }

# Global singleton instance
scan_history = ScanHistoryManager()
