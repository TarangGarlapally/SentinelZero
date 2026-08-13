import os
import sys
import json
import threading

# Force UTF-8 stdout encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

from core.file_locker import FileLocker
from core.scanners.universal_scanner import UniversalScanner
from core.watchdog_engine import WatchdogEngine
from core.cookie_guard import CookieGuard
from gui.tray_gui import SystemTrayApp
from gui.quarantine_window import QuarantineWindow
from utils.autostart import set_autostart

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    print("=" * 60)
    print("      Sentinel Zero - Proactive System Guard v1.0")
    print("=" * 60)

    config = load_config()
    
    # 1. Enable Windows Autostart
    set_autostart(True, os.path.join(BASE_DIR, "app.py"))

    # 2. Initialize Core Engines
    quarantine_dir = config.get("quarantine_dir", os.path.join(BASE_DIR, "Quarantine"))
    locker = FileLocker(quarantine_dir)
    scanner = UniversalScanner()

    # 3. Setup System Tray & Notifications
    tray = SystemTrayApp(
        on_open_quarantine=lambda: open_quarantine_gui(quarantine_dir),
        on_exit=lambda: stop_all(watchdog, cookie_guard)
    )

    # 4. Initialize Real-Time Watchdog Engine for Downloads
    watch_paths = config.get("watch_directories", [])
    watchdog = WatchdogEngine(
        watch_paths=watch_paths,
        locker=locker,
        scanner=scanner,
        notify_callback=tray.show_notification
    )
    watchdog.start()

    # 5. Initialize Cookie Guard
    cookie_paths = config.get("cookie_guard", {}).get("browser_cookie_paths", [])
    cookie_guard = CookieGuard(
        cookie_paths=cookie_paths,
        callback_alert=tray.show_notification
    )
    cookie_guard.start()

    tray.show_notification("Sentinel Zero Active", "Real-Time Universal Lock & Cookie Guard Enabled.")

    # 6. Run System Tray Icon Loop
    try:
        tray.run()
    except KeyboardInterrupt:
        stop_all(watchdog, cookie_guard)

def open_quarantine_gui(quarantine_dir):
    def _run():
        app = QuarantineWindow(quarantine_dir)
        app.mainloop()
    threading.Thread(target=_run, daemon=True).start()

def stop_all(watchdog, cookie_guard):
    print("[Sentinel Zero] Stopping security engines...")
    if watchdog:
        watchdog.stop()
    if cookie_guard:
        cookie_guard.stop()
    sys.exit(0)

if __name__ == "__main__":
    main()
