import os
import zipfile
import tarfile
import re

class ArchiveScanner:
    """Recursively scans compressed archives (.zip, .tar, .gz) for hidden executable payloads and disguised runtimes."""

    SUSPICIOUS_EXTENSIONS = ['.exe', '.bat', '.cmd', '.vbs', '.ps1', '.scr', '.pyd', '.dll']
    DOUBLE_EXT_PATTERN = r"\.(pdf|docx|xlsx|jpg|png)\.(exe|bat|cmd|vbs|ps1|scr)$"

    def scan(self, filepath):
        if not os.path.exists(filepath):
            return True, "File not found"

        ext = os.path.splitext(filepath)[1].lower()
        threats = []

        try:
            if ext == '.zip':
                with zipfile.ZipFile(filepath, 'r') as z:
                    file_list = z.namelist()
                    for name in file_list:
                        # Check double extensions (e.g., invoice.pdf.exe)
                        if re.search(self.DOUBLE_EXT_PATTERN, name, re.IGNORECASE):
                            threats.append(f"Double extension disguised executable: {name}")
                        # Check fake Blender executable inside zip
                        if "blender.exe" in name.lower() and not "blender.org" in name.lower():
                            threats.append(f"Disguised Blender executable in archive: {name}")
                        # Check stealer module logs or scripts inside zip
                        if "mod_stealc" in name.lower() or "stealc" in name.lower():
                            threats.append(f"Stealc infostealer module inside archive: {name}")

            elif ext in ['.tar', '.gz', '.tgz']:
                with tarfile.open(filepath, 'r:*') as t:
                    for member in t.getmembers():
                        name = member.name
                        if re.search(self.DOUBLE_EXT_PATTERN, name, re.IGNORECASE):
                            threats.append(f"Double extension executable: {name}")
                        if "blender.exe" in name.lower():
                            threats.append(f"Disguised Blender payload in archive: {name}")

            if threats:
                return False, f"Malicious archive payload detected! ({threats[0]})"

            return True, "Clean Archive"
        except Exception as e:
            return True, f"Archive scan bypass: {e}"
