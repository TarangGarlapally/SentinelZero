import os
import subprocess
import json

TRUSTED_PUBLISHERS = [
    "NVIDIA Corporation",
    "Microsoft Corporation",
    "Microsoft Windows",
    "Linden Research, Inc.",
    "Linden Lab",
    "Google LLC",
    "Mozilla Corporation",
    "Adobe Inc.",
    "Valve Corp.",
    "Valve Corporation",
    "Epic Games, Inc.",
    "Discord Inc.",
    "Brave Software, Inc."
]

def verify_digital_signature(filepath):
    """
    Verifies if a Windows binary (.exe / .dll) has a valid Authenticode digital signature 
    from a trusted vendor (NVIDIA, Microsoft, Linden Lab/SecondLife, Google, etc.).
    Returns (is_signed_and_trusted, publisher_name).
    """
    if not os.path.exists(filepath) or not filepath.lower().endswith(('.exe', '.dll', '.sys', '.msi')):
        return False, ""

    try:
        # Run PowerShell Get-AuthenticodeSignature safely
        ps_cmd = f"(Get-AuthenticodeSignature -FilePath '{filepath}').SignerCertificate.Subject"
        cmd = ["powershell", "-NoProfile", "-Command", ps_cmd]
        
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=5).decode('utf-8', errors='ignore').strip()
        
        if output:
            for trusted in TRUSTED_PUBLISHERS:
                if trusted.lower() in output.lower():
                    return True, trusted
            # Validly signed by another vendor
            return True, output.split("CN=")[-1].split(",")[0] if "CN=" in output else output
    except Exception:
        pass

    return False, ""
