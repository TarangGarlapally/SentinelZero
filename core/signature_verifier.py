import os
import subprocess
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WHITELIST_FILE = os.path.join(BASE_DIR, "..", "user_whitelist.json")

def load_user_whitelist():
    """Loads user-whitelisted application paths or filenames."""
    if os.path.exists(WHITELIST_FILE):
        try:
            with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("allowed_files", []))
        except Exception:
            pass
    return set()

def add_to_whitelist(filepath_or_name):
    """Adds a file path or filename to the user whitelist."""
    allowed = load_user_whitelist()
    allowed.add(filepath_or_name.lower())
    try:
        with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
            json.dump({"allowed_files": list(allowed)}, f, indent=2)
        return True
    except Exception:
        return False

def verify_digital_signature(filepath):
    """
    Universal Windows Authenticode Verifier:
    Verifies if ANY Windows binary (.exe / .dll / .msi) has a valid, untampered 
    digital signature issued by ANY recognized Certificate Authority on Earth, 
    OR is present in the local user whitelist.
    
    Returns (is_trusted, publisher_or_reason).
    """
    if not os.path.exists(filepath):
        return False, ""

    filename = os.path.basename(filepath).lower()

    # 1. User Custom Whitelist Check
    allowed_set = load_user_whitelist()
    if filepath.lower() in allowed_set or filename in allowed_set:
        return True, "User Whitelisted Application"

    if not filepath.lower().endswith(('.exe', '.dll', '.sys', '.msi')):
        return False, ""

    # 2. Universal Windows Authenticode Signature Verification
    try:
        # Check if Windows Authenticode Status is 'Valid'
        ps_cmd = f"$sig = Get-AuthenticodeSignature -FilePath '{filepath}'; if ($sig.Status -eq 'Valid') {{ Write-Output ('VALID:' + $sig.SignerCertificate.Subject) }} else {{ Write-Output 'INVALID' }}"
        cmd = ["powershell", "-NoProfile", "-Command", ps_cmd]
        
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=5).decode('utf-8', errors='ignore').strip()
        
        if output.startswith("VALID:"):
            subject = output[6:]
            publisher = subject.split("CN=")[-1].split(",")[0] if "CN=" in subject else subject
            return True, publisher
    except Exception:
        pass

    return False, ""
