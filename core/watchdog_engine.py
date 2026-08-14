import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .scan_history import scan_history

class BrowserDownloadHandler(FileSystemEventHandler):
    """
    Universal Browser Download Interceptor:
    Monitors all system folders for completed web browser downloads.
    Silently unlocks clean files without annoying popup notifications, 
    while recording both Safe Scans and Blocked Threats in the Security Log.
    Popups trigger ONLY when genuine malware/threats are blocked.
    """

    TEMP_DOWNLOAD_EXTENSIONS = ['.crdownload', '.part', '.tmp', '.download']

    def __init__(self, locker, scanner, notify_callback=None):
        self.locker = locker
        self.scanner = scanner
        self.notify_callback = notify_callback
        self._recently_scanned = set()

    def _is_browser_download(self, src_path, dest_path):
        """Checks if event represents a completed browser download."""
        src_ext = os.path.splitext(src_path)[1].lower() if src_path else ""
        dest_ext = os.path.splitext(dest_path)[1].lower() if dest_path else ""

        # Pattern 1: Browser finished downloading and renamed .crdownload / .part / .tmp -> final file
        if src_ext in self.TEMP_DOWNLOAD_EXTENSIONS and dest_ext not in self.TEMP_DOWNLOAD_EXTENSIONS:
            return True

        # Pattern 2: Windows Mark-of-the-Web (Zone.Identifier) attached by browser
        if dest_path:
            zone_file = dest_path + ":Zone.Identifier"
            if os.path.exists(zone_file):
                return True

        return False

    def _process_completed_download(self, filepath):
        if not os.path.exists(filepath) or os.path.isdir(filepath):
            return

        # Ignore internal IDE/system files
        if ".git" in filepath or "__pycache__" in filepath or filepath.endswith(".gitkeep"):
            return

        if filepath in self._recently_scanned:
            return

        self._recently_scanned.add(filepath)
        filename = os.path.basename(filepath)

        # 1. Instantly Lock Downloaded File
        locked, handle = self.locker.lock_file(filepath)

        # 2. Universal Threat Scan
        is_clean, result_msg = self.scanner.scan_file(filepath)

        if is_clean:
            # 3A. Unlock clean file silently & record SAFE entry in activity history
            self.locker.unlock_file(filepath)
            scan_history.record_scan(filepath, "SAFE", result_msg)
        else:
            # 3B. Block threat, move to quarantine, record QUARANTINED log, and trigger alert
            quarantine_path = self.locker.quarantine_file(filepath, threat_info=result_msg)
            scan_history.record_scan(filepath, "QUARANTINED", result_msg)
            if self.notify_callback:
                self.notify_callback("🚨 THREAT BLOCKED & QUARANTINED!", f"Blocked: {filename}\n{result_msg}")

        # Clean cache after 10s
        threading.Timer(10.0, lambda: self._recently_scanned.discard(filepath)).start()

    def on_moved(self, event):
        """Fired when browser completes download and renames .crdownload / .part -> final filename."""
        if not event.is_directory:
            if self._is_browser_download(event.src_path, event.dest_path):
                threading.Thread(target=self._process_completed_download, args=(event.dest_path,), daemon=True).start()

    def on_created(self, event):
        """Fired for direct downloads or downloads with instant Mark-of-the-Web."""
        if not event.is_directory:
            if self._is_browser_download(None, event.src_path):
                threading.Thread(target=self._process_completed_download, args=(event.src_path,), daemon=True).start()


class WatchdogEngine:
    """Monitors configured user directories for web browser download completions."""

    def __init__(self, watch_paths, locker, scanner, notify_callback=None):
        self.watch_paths = watch_paths
        self.observer = Observer()
        self.handler = BrowserDownloadHandler(locker, scanner, notify_callback)

    def start(self):
        for path in self.watch_paths:
            if os.path.exists(path):
                self.observer.schedule(self.handler, path, recursive=True)
                print(f"[WatchdogEngine] Watching for Browser Downloads in: {path}")
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()
