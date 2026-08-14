import os
import threading
from PIL import Image, ImageDraw
import pystray

def create_tray_icon():
    """Generates a dark-mode shield icon dynamically in memory."""
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # Draw Shield background
    draw.polygon([(32, 4), (58, 16), (58, 42), (32, 60), (6, 42), (6, 16)], fill=(20, 30, 45, 255), outline=(0, 210, 255, 255), width=3)
    # Draw Z for Sentinel Zero
    draw.line([(22, 22), (42, 22), (22, 42), (42, 42)], fill=(0, 210, 255, 255), width=4)
    return image

class SystemTrayApp:
    """Manages the Windows Notification Area tray icon & desktop toast alerts."""

    def __init__(self, on_open_quarantine=None, on_exit=None):
        self.on_open_quarantine = on_open_quarantine
        self.on_exit = on_exit
        self.icon = None

    def show_notification(self, title, message):
        """Displays native Windows notification with safe error handling via pystray."""
        print(f"[Sentinel Zero] {title}: {message}")
        try:
            if self.icon and hasattr(self.icon, 'notify'):
                self.icon.notify(message, title)
        except Exception:
            pass

    def run(self):
        icon_img = create_tray_icon()
        menu = pystray.Menu(
            pystray.MenuItem("🛡️ Sentinel Zero (Active)", lambda: None, enabled=False),
            pystray.MenuItem("Vault & Quarantined Threats", self._open_vault),
            pystray.MenuItem("Exit Sentinel Zero", self._quit)
        )
        self.icon = pystray.Icon("SentinelZero", icon_img, "Sentinel Zero Guard", menu)
        self.icon.run()

    def _open_vault(self):
        if self.on_open_quarantine:
            self.on_open_quarantine()

    def _quit(self):
        if self.icon:
            self.icon.stop()
        if self.on_exit:
            self.on_exit()
