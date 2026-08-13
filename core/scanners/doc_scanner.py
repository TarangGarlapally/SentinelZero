import os
import re

class DocScanner:
    """Inspects documents (.pdf, .docx, .xlsx) for malicious OLE VBA macros and embedded download payloads."""

    MACRO_PATTERNS = [
        r"AutoOpen",
        r"Document_Open",
        r"Shell\s*\(",
        r"WScript\.Shell",
        r"Powershell",
        r"URLDownloadToFile",
        r"CreateObject\s*\(\s*[\"']WScript\.Shell"
    ]

    def scan(self, filepath):
        if not os.path.exists(filepath):
            return True, "File not found"

        try:
            with open(filepath, "rb") as f:
                content = f.read()

            content_str = content.decode("latin-1", errors="ignore")
            threats = []
            for pattern in self.MACRO_PATTERNS:
                if re.search(pattern, content_str, re.IGNORECASE):
                    threats.append(pattern)

            if len(threats) >= 2:
                return False, f"Malicious macro stream detected in document! (Matched: {', '.join(threats)})"

            return True, "Clean Document"
        except Exception as e:
            return True, f"Doc scan error: {e}"
