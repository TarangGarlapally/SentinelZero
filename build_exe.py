import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def build():
    print("============================================================")
    print("      Sentinel Zero - Building Standalone Windows .EXE")
    print("============================================================")

    # Install pyinstaller if missing
    try:
        import PyInstaller
    except ImportError:
        print("[*] Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=SentinelZero",
        f"--add-data={os.path.join(BASE_DIR, 'rules')};rules",
        f"--add-data={os.path.join(BASE_DIR, 'config.example.json')};.",
        os.path.join(BASE_DIR, "app.py")
    ]

    print(f"[*] Executing PyInstaller build command...")
    subprocess.check_call(cmd)
    print(f"[✅ SUCCESS] Standalone build complete! Output folder: {os.path.join(BASE_DIR, 'dist', 'SentinelZero')}")

if __name__ == "__main__":
    build()
