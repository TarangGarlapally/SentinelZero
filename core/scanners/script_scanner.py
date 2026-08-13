import re
import os

class ScriptScanner:
    """Multi-language static analyzer for Python, PowerShell, Batch, VBScript, and JavaScript files."""

    DANGEROUS_TRIGGERS = [
        r"urllib\.request",
        r"requests\.(get|post)",
        r"Invoke-WebRequest",
        r"WScript\.Shell",
        r"powershell.*-enc",
        r"exec\s*\(",
        r"eval\s*\(",
        r"base64\.b64decode",
        r"mod-stealc\.py",
        r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",  # IP addresses
        r"sqlite3.*cookies",
        r"CryptUnprotectData"
    ]

    def scan(self, filepath):
        if not os.path.exists(filepath):
            return True, "File not found"

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            matches = []
            for trigger in self.DANGEROUS_TRIGGERS:
                found = re.findall(trigger, content, re.IGNORECASE)
                if found:
                    matches.append(trigger)

            if len(matches) >= 1:
                return False, f"Malicious script payload detected! Triggered signatures: {', '.join(matches[:3])}"

            return True, "Clean script file"
        except Exception as e:
            return True, f"Script scan error: {e}"
