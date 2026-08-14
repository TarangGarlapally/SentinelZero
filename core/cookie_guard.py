import os
import psutil
import time
import threading
from .signature_verifier import verify_digital_signature

class CookieGuard:
    """
    Dynamic Browser Cookie Guard:
    Monitors browser Cookies databases and automatically verifies processes attempting access.
    Uses Windows Authenticode Digital Signatures to dynamically trust ALL legitimate signed applications 
    (Microsoft Edge, WebView2, Chrome, Brave, Antigravity, VS Code, Firefox, etc.) without manual whitelist maintenance!
    ONLY blocks unsigned stealer binaries attempting to harvest session tokens.
    """

    def __init__(self, cookie_paths, callback_alert=None):
        self.cookie_paths = cookie_paths
        self.callback_alert = callback_alert
        self.running = False
        self._thread = None
        self._trusted_pids = set()

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def _monitor_loop(self):
        while self.running:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'exe', 'open_files']):
                    pid = proc.info['pid']
                    if pid in self._trusted_pids:
                        continue

                    pname = proc.info.get('name')
                    exe_path = proc.info.get('exe')
                    open_files = proc.info.get('open_files')

                    if open_files and exe_path:
                        for f in open_files:
                            file_path = f.path
                            for cpath in self.cookie_paths:
                                if cpath.lower() in file_path.lower() or ("\\user data\\" in file_path.lower() and "cookies" in file_path.lower()):
                                    # 1. Dynamic Authenticode Signature Verification
                                    is_signed, publisher = verify_digital_signature(exe_path)
                                    if is_signed:
                                        # Legitimate signed app (Microsoft, Google, Antigravity, etc.) -> Cache as trusted
                                        self._trusted_pids.add(pid)
                                        break

                                    # 2. Unsigned binary attempting to read browser cookies database!
                                    threat_msg = f"Unsigned process '{pname}' (PID {pid}) attempted to harvest browser session cookies!"
                                    print(f"[CookieGuard] ALERT: {threat_msg}")
                                    
                                    # Terminate stealer process
                                    try:
                                        proc.kill()
                                    except Exception:
                                        pass

                                    if self.callback_alert:
                                        self.callback_alert("🚨 Infostealer Intercepted!", threat_msg)
            except Exception:
                pass
            time.sleep(1.0)
