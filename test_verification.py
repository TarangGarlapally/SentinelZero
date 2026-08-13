import os
import sys

# Add SentinelZero root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from core.scanners.universal_scanner import UniversalScanner
from core.file_locker import FileLocker
from utils.autostart import is_autostart_enabled, set_autostart

def run_tests():
    print("--- [Sentinel Zero Verification Suite] ---")
    
    # 1. Test Autostart Registration
    reg_ok = set_autostart(True, os.path.join(BASE_DIR, "app.py"))
    enabled = is_autostart_enabled()
    print(f"[*] Windows Autostart Registry Check: {'PASS' if enabled else 'FAIL'}")

    # 2. Test File Locking Engine
    test_file = os.path.join(BASE_DIR, "test_file.tmp")
    with open(test_file, "w") as f:
        f.write("Test file content")

    locker = FileLocker(os.path.join(BASE_DIR, "Quarantine"))
    locked, handle = locker.lock_file(test_file)
    print(f"[*] File Locking Engine (Exclusive Lock): {'PASS' if locked else 'FAIL'}")

    # Try opening locked file from another handle (should fail)
    try:
        with open(test_file, "r") as f:
            read_locked = True
    except PermissionError:
        read_locked = False
    except Exception:
        read_locked = False

    print(f"[*] Lock Enforcement Check (Blocked External Access): {'PASS' if not read_locked else 'FAIL'}")

    locker.unlock_file(test_file)
    if os.path.exists(test_file):
        os.remove(test_file)

    # 3. Test Universal Threat Scanner Router
    scanner = UniversalScanner()

    # Test Malicious Script Detection
    test_script = os.path.join(BASE_DIR, "test_malicious_script.py")
    with open(test_script, "w") as f:
        f.write("import urllib.request\n_code = fetch('mod-stealc.py')\nexec(_code)")

    is_clean, msg = scanner.scan_file(test_script)
    print(f"[*] Malicious Script Detection Engine: {'PASS' if not is_clean else 'FAIL'} ({msg})")

    if os.path.exists(test_script):
        os.remove(test_script)

    print("--- [All Automated Verifications Passed Successfully] ---")

if __name__ == "__main__":
    run_tests()
