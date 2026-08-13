import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DownloadHandler(FileSystemEventHandler):
    """Event handler that locks, scans, and unlocks/quarantines any newly created or renamed file."""

    def __init__(self, locker, scanner, notify_callback=None):
        self.locker = locker
        self.scanner = scanner
        self.notify_callback = notify_callback
        self._recently_scanned = set()

    def _process_file(self, filepath):
        if not os.path.exists(filepath) or os.path.isdir(filepath):
            return

        # Ignore temporary partial download files (.crdownload, .part, .tmp) until download completes
        ext = os.path.splitext(filepath)[1].lower()
        if ext in ['.crdownload', '.part', '.tmp', '.download']:
            return

        if filepath in self._recently_scanned:
            return

        self._recently_scanned.add(filepath)
        filename = os.path.basename(filepath)

        # 1. Instantly Lock File
        locked, handle = self.locker.lock_file(filepath)
        if self.notify_callback:
            self.notify_callback("🔒 File Locked & Scanning", f"Scanning: {filename}")

        # 2. Universal Threat Scan
        is_clean, result_msg = self.scanner.scan_file(filepath)

        if is_clean:
            # 3A. Unlock clean file
            self.locker.unlock_file(filepath)
            if self.notify_callback:
                self.notify_callback("✅ File Verified Safe", f"Unlocked: {filename}\n({result_msg})")
        else:
            # 3B. Quarantine threat file
            quarantine_path = self.locker.quarantine_file(filepath, threat_info=result_msg)
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
    """Manages real-time filesystem observers across all configured directories."""

    def __init__(self, watch_paths, locker, scanner, notify_callback=None):
        self.watch_paths = watch_paths
        self.observer = Observer()
        self.handler = DownloadHandler(locker, scanner, notify_callback)

    def start(self):
        for path in self.watch_paths:
            if os.path.exists(path):
                self.observer.schedule(self.handler, path, recursive=True)
                print(f"[WatchdogEngine] Watching: {path}")
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()
