import os
import sys
import json
import threading

# Force UTF-8 stdout encoding for Windows console (safely check if sys.stdout exists for PyInstaller windowed mode)
if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    except Exception:
        pass

from core.file_locker import FileLocker
from core.scanners.universal_scanner import UniversalScanner
from core.watchdog_engine import WatchdogEngine
from core.cookie_guard import CookieGuard
from gui.tray_gui import SystemTrayApp
from gui.quarantine_window import QuarantineWindow
from gui.web_dashboard import run_dashboard_bg
from utils.feed_updater import FeedUpdater
from utils.autostart import set_autostart

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "app_name": "Sentinel Zero",
        "version": "1.4.1",
        "autostart_enabled": True,
        "quarantine_dir": os.path.join(BASE_DIR, "Quarantine"),
        "watch_mode": "ALL",
        "watch_directories": [os.path.expanduser("~")],
        "custom_watch_directories": [
            os.path.expanduser(r"~\Downloads"),
            os.path.expanduser(r"~\Desktop"),
            os.path.expanduser(r"~\Documents")
        ],
        "cookie_guard": {"enabled": True, "browser_cookie_paths": []}
    }

def main():
    print("=" * 60)
    print("      Sentinel Zero - Proactive System Guard v1.4.2")
    print("=" * 60)

    config = load_config()
    
    # 1. Enable Windows Autostart
    set_autostart(True, os.path.join(BASE_DIR, "app.py"))

    # 2. Sync Latest Infostealer Signatures
    updater = FeedUpdater()
    threading.Thread(target=updater.update_rules, daemon=True).start()

    # 3. Initialize Core Engines
    quarantine_dir = config.get("quarantine_dir", os.path.join(BASE_DIR, "Quarantine"))
    locker = FileLocker(quarantine_dir)
    scanner = UniversalScanner(vt_api_key=config.get("virustotal_api_key"))

    # 4. Setup System Tray & Notifications
    tray = SystemTrayApp(
        on_open_quarantine=lambda: open_quarantine_gui(quarantine_dir),
        on_exit=lambda: stop_all(watchdog, cookie_guard)
    )

    # 5. Initialize Real-Time Watchdog Engine for Downloads
    watch_paths = config.get("watch_directories", [os.path.expanduser("~")])
    watchdog = WatchdogEngine(
        watch_paths=watch_paths,
        locker=locker,
        scanner=scanner,
        notify_callback=tray.show_notification
    )
    watchdog.start()

    # Callback when folder configuration is updated from Web Dashboard
    def handle_config_update(new_config):
        new_paths = new_config.get("watch_directories", [])
        print(f"[Sentinel Zero] Updating folder monitoring targets: {new_paths}")
        watchdog.update_watch_paths(new_paths)

    # 6. Start Local Web Dashboard (http://localhost:9090) with Config Callback
    run_dashboard_bg(port=9090, on_config_updated=handle_config_update)

    # 7. Initialize Cookie Guard
    cookie_paths = config.get("cookie_guard", {}).get("browser_cookie_paths", [])
    cookie_guard = CookieGuard(
        cookie_paths=cookie_paths,
        callback_alert=tray.show_notification
    )
    cookie_guard.start()

    tray.show_notification("Sentinel Zero Active", "Universal Lock & Web Dashboard (http://localhost:9090) Running.")

    # 8. Run System Tray Icon Loop
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
