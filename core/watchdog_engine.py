import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .scan_history import scan_history

class DownloadHandler(FileSystemEventHandler):
    """Event handler that locks, scans, and unlocks/quarantines ANY newly downloaded file."""

    IGNORE_EXTENSIONS = ['.crdownload', '.part', '.tmp', '.download', '.git', '.pyc', '.log', '.json', '.gitkeep']

    def __init__(self, locker, scanner, notify_callback=None):
        self.locker = locker
        self.scanner = scanner
        self.notify_callback = notify_callback
        self._recently_scanned = set()

    def _process_file(self, filepath):
        if not os.path.exists(filepath) or os.path.isdir(filepath):
            return

        # Ignore temporary partial download files & system files
        ext = os.path.splitext(filepath)[1].lower()
        if ext in self.IGNORE_EXTENSIONS or ".git" in filepath or "__pycache__" in filepath:
            return

        if filepath in self._recently_scanned:
            return

        self._recently_scanned.add(filepath)
        filename = os.path.basename(filepath)

        # 1. Instantly Lock Downloaded File
        locked, handle = self.locker.lock_file(filepath)
        if self.notify_callback:
            self.notify_callback("🔒 New Download Locked & Scanning", f"Scanning: {filename}")

        # 2. Universal Threat Scan
        is_clean, result_msg = self.scanner.scan_file(filepath)

        if is_clean:
            # 3A. Unlock clean file & record in history
            self.locker.unlock_file(filepath)
            scan_history.record_scan(filepath, "SAFE", result_msg)
            if self.notify_callback:
                self.notify_callback("✅ Download Verified Safe", f"Unlocked: {filename}\n({result_msg})")
        else:
            # 3B. Quarantine threat file & record in history
            quarantine_path = self.locker.quarantine_file(filepath, threat_info=result_msg)
            scan_history.record_scan(filepath, "QUARANTINED", result_msg)
            if self.notify_callback:
                self.notify_callback("🚨 THREAT BLOCKED & QUARANTINED!", f"Quarantined: {filename}\n{result_msg}")

        # Clean cache after 10s
        threading.Timer(10.0, lambda: self._recently_scanned.discard(filepath)).start()

    def on_created(self, event):
        if not event.is_directory:
            threading.Thread(target=self._process_file, args=(event.src_path,), daemon=True).start()

    def on_moved(self, event):
        if not event.is_directory:
            # Triggered when Chrome/Brave/Edge finishes .crdownload -> final file rename
            threading.Thread(target=self._process_file, args=(event.dest_path,), daemon=True).start()


class WatchdogEngine:
    """Manages real-time filesystem observers restricted strictly to User Downloads."""

    def __init__(self, watch_paths, locker, scanner, notify_callback=None):
        self.watch_paths = watch_paths
        self.observer = Observer()
        self.handler = DownloadHandler(locker, scanner, notify_callback)

    def start(self):
        for path in self.watch_paths:
            if os.path.exists(path):
                # Watch Downloads folder without walking into internal project/build subtrees
                self.observer.schedule(self.handler, path, recursive=False)
                print(f"[WatchdogEngine] Watching User Downloads: {path}")
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()
