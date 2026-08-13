import sys
import winreg
import os

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "SentinelZeroGuard"

def set_autostart(enable=True, script_path=None):
    """Registers or unregisters Sentinel Zero in Windows Boot Registry."""
    if script_path is None:
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.py"))

    # Command to run python w/ app.py in background
    cmd = f'"{sys.executable}" "{script_path}" --autostart'

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        if enable:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
            print(f"[Autostart] Registered in Windows Registry: {cmd}")
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
                print(f"[Autostart] Unregistered from Windows Registry.")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"[Autostart] Registry error: {e}")
        return False

def is_autostart_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False
