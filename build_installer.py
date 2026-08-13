import os
import sys
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
BUILD_DIR = os.path.join(BASE_DIR, "build")

def main():
    print("============================================================")
    print("      Sentinel Zero - Building Standalone Windows Setup Package")
    print("============================================================")

    # 1. Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("[*] Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Clean old build artifacts
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR, ignore_errors=True)
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR, ignore_errors=True)

    # 2. PyInstaller Build Command
    rules_data = f"{os.path.join(BASE_DIR, 'rules')};rules"
    config_data = f"{os.path.join(BASE_DIR, 'config.example.json')};."

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",               # Build single standalone .exe installer!
        "--windowed",              # Run in GUI mode without opening command console window!
        "--name=SentinelZero-Setup",
        f"--add-data={rules_data}",
        f"--add-data={config_data}",
        os.path.join(BASE_DIR, "app.py")
    ]

    print(f"[*] Compiling standalone binary SentinelZero-Setup.exe...")
    subprocess.check_call(cmd)

    exe_path = os.path.join(DIST_DIR, "SentinelZero-Setup.exe")
    if os.path.exists(exe_path):
        print("=" * 60)
        print(f"[SUCCESS] Standalone Windows Installer Created!")
        print(f"Location: {exe_path}")
        print("Double-click SentinelZero-Setup.exe to run Sentinel Zero directly as a native Windows App!")
        print("=" * 60)
    else:
        print("[!] Build failed to generate executable.")

if __name__ == "__main__":
    main()
