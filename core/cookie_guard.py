import os
import psutil
import time
import threading
import pywintypes
import win32file
import win32con

class CookieGuard:
    """Monitors browser Cookies databases and terminates non-browser processes attempting to access session tokens."""

    ALLOWED_BROWSER_PROCESSES = [
        "chrome.exe",
        "msedge.exe",
        "brave.exe",
        "firefox.exe",
        "opera.exe",
        "python.exe"  # Allow Sentinel Zero daemon
    ]

    def __init__(self, cookie_paths, callback_alert=None):
        self.cookie_paths = cookie_paths
        self.callback_alert = callback_alert
        self.running = False
        self._thread = None

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def _monitor_loop(self):
        while self.running:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'open_files']):
                    pname = proc.info['name']
                    if pname and pname.lower() not in self.ALLOWED_BROWSER_PROCESSES:
                        open_files = proc.info.get('open_files')
                        if open_files:
                            for f in open_files:
                                file_path = f.path
                                for cpath in self.cookie_paths:
                                    if cpath.lower() in file_path.lower() or "cookies" in file_path.lower():
                                        # Unauthorized process accessing cookies database!
                                        threat_msg = f"Unauthorized process '{pname}' (PID {proc.info['pid']}) attempted to read browser cookies!"
                                        print(f"[CookieGuard] ALERT: {threat_msg}")
                                        
                                        # Kill unauthorized stealer process immediately
                                        try:
                                            proc.kill()
                                        except Exception:
                                            pass

                                        if self.callback_alert:
                                            self.callback_alert("🚨 Cookie Theft Intercepted!", threat_msg)
            except Exception:
                pass
            time.sleep(1.0)
