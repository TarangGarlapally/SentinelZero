import os
import sys
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
BUILD_DIR = os.path.join(BASE_DIR, "build")
ISCC_PATH = r"C:\Users\taran\AppData\Local\Programs\Inno Setup 6\ISCC.exe"

def main():
    print("============================================================")
    print("      Sentinel Zero - Building Professional Windows App Package")
    print("============================================================")

    # 1. PyInstaller Build Command (--onedir mode for clean DLL/binary packaging)
    rules_data = f"{os.path.join(BASE_DIR, 'rules')};rules"
    config_data = f"{os.path.join(BASE_DIR, 'config.example.json')};."

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",                # Clean app directory bundle
        "--windowed",              # Run in background GUI mode with NO CMD console window!
        "--name=SentinelZero",     # Native Process Name: SentinelZero.exe
        "--uac-admin",             # Embed Administrator UAC Manifest
        f"--add-data={rules_data}",
        f"--add-data={config_data}",
        os.path.join(BASE_DIR, "app.py")
    ]

    print("[*] Step 1: Compiling native executable SentinelZero.exe...")
    subprocess.check_call(cmd)

    # 2. Inno Setup Compiler Step
    iss_file = os.path.join(BASE_DIR, "installer", "SentinelZero.iss")
    if os.path.exists(ISCC_PATH) and os.path.exists(iss_file):
        print("[*] Step 2: Compiling professional Windows Setup Wizard (SentinelZero-Installer.exe)...")
        subprocess.check_call([ISCC_PATH, iss_file])
        
        installer_exe = os.path.join(DIST_DIR, "SentinelZero-Installer.exe")
        if os.path.exists(installer_exe):
            print("=" * 60)
            print("[SUCCESS] Professional Windows Setup Wizard Created!")
            print(f"Installer Path: {installer_exe}")
            print("Double-click SentinelZero-Installer.exe to run the setup wizard, grant permissions, and install to Program Files!")
            print("=" * 60)

if __name__ == "__main__":
    main()
