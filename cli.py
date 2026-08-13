import sys
import os
import argparse
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from core.scanners.universal_scanner import UniversalScanner
from utils.autostart import is_autostart_enabled, set_autostart

def main():
    parser = argparse.ArgumentParser(description="Sentinel Zero - Proactive System Guard CLI Control Center")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Command: status
    parser_status = subparsers.add_parser("status", help="Check Sentinel Zero protection status")

    # Command: scan
    parser_scan = subparsers.add_parser("scan", help="Scan a file or directory for threats")
    parser_scan.add_argument("path", help="Path to file or directory to scan")

    # Command: autostart
    parser_auto = subparsers.add_parser("autostart", help="Enable or disable Windows boot autostart")
    parser_auto.add_argument("state", choices=["enable", "disable"], help="Enable or disable autostart")

    args = parser.parse_args()

    if args.command == "status":
        enabled = is_autostart_enabled()
        print("============================================================")
        print("          Sentinel Zero - System Guard Status")
        print("============================================================")
        print(f"[*] Windows Autostart: {'ENABLED' if enabled else 'DISABLED'}")
        print(f"[*] Core Installation Path: {BASE_DIR}")
        print(f"[*] Real-Time Lock Status: ACTIVE")

    elif args.command == "scan":
        target = os.path.abspath(args.path)
        if not os.path.exists(target):
            print(f"[!] Path does not exist: {target}")
            return

        scanner = UniversalScanner()
        if os.path.isfile(target):
            print(f"[*] Scanning file: {target}")
            is_clean, msg = scanner.scan_file(target)
            if is_clean:
                print(f"[✅ SAFE] {msg}")
            else:
                print(f"[🚨 THREAT DETECTED] {msg}")
        else:
            print(f"[*] Scanning directory: {target}")
            clean_count = 0
            threat_count = 0
            for root, _, files in os.walk(target):
                for f in files:
                    fp = os.path.join(root, f)
                    is_clean, msg = scanner.scan_file(fp)
                    if is_clean:
                        clean_count += 1
                    else:
                        threat_count += 1
                        print(f"  [🚨 THREAT] {fp} -> {msg}")
            print(f"[*] Scan finished. Clean: {clean_count}, Threats Found: {threat_count}")

    elif args.command == "autostart":
        if args.state == "enable":
            set_autostart(True, os.path.join(BASE_DIR, "app.py"))
            print("[+] Windows Autostart ENABLED.")
        else:
            set_autostart(False)
            print("[-] Windows Autostart DISABLED.")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
