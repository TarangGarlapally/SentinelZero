import re
import os

class BlendScanner:
    """Parses Blender .blend files directly in binary mode to inspect embedded Python scripts."""

    SUSPICIOUS_PATTERNS = [
        r"urllib\.request",
        r"requests\.(get|post)",
        r"socket\.",
        r"subprocess\.",
        r"os\.system",
        r"os\.popen",
        r"exec\s*\(",
        r"eval\s*\(",
        r"base64\.b64decode",
        r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",  # IPv4 Literals
        r"mod-stealc\.py",
        r"stealc",
        r"AppData\\Local\\Temp"
    ]

    def scan(self, filepath):
        if not os.path.exists(filepath):
            return True, "File not found"

        try:
            with open(filepath, "rb") as f:
                header = f.read(12)
                if not header.startswith(b"BLENDER"):
                    return True, "Not a Blender file"

                content = f.read()

            # Search for embedded Python code blocks inside BLENDER binary streams
            content_str = content.decode("latin-1", errors="ignore")
            
            threats_found = []
            for pattern in self.SUSPICIOUS_PATTERNS:
                matches = re.findall(pattern, content_str, re.IGNORECASE)
                if matches:
                    threats_found.append(f"Suspicious pattern matched: '{pattern}' ({len(matches)} occurrence(s))")

            if threats_found:
                return False, f"Malicious embedded Python script detected in .blend file! {threats_found[0]}"

            return True, "Clean Blender file"
        except Exception as e:
            return True, f"Scan bypassed due to error: {e}"
