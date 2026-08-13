import os
from .blend_scanner import BlendScanner
from .pe_scanner import PEScanner
from .script_scanner import ScriptScanner
from .archive_scanner import ArchiveScanner
from .doc_scanner import DocScanner

class UniversalScanner:
    """Universal threat router for ANY file type downloaded or created on the system."""

    def __init__(self):
        self.blend_scanner = BlendScanner()
        self.pe_scanner = PEScanner()
        self.script_scanner = ScriptScanner()
        self.archive_scanner = ArchiveScanner()
        self.doc_scanner = DocScanner()

    def scan_file(self, filepath):
        if not os.path.exists(filepath):
            return True, "File no longer exists"

        ext = os.path.splitext(filepath)[1].lower()

        # Check binary magic bytes for accurate format identification
        try:
            with open(filepath, "rb") as f:
                header = f.read(16)
        except Exception as e:
            return True, f"Cannot open file for header check: {e}"

        # 1. PE Executables (.exe, .dll, .msi, .scr, .sys)
        if header.startswith(b"MZ") or ext in ['.exe', '.dll', '.msi', '.scr', '.sys']:
            return self.pe_scanner.scan(filepath)

        # 2. Blender files (.blend)
        if header.startswith(b"BLENDER") or ext == '.blend':
            return self.blend_scanner.scan(filepath)

        # 3. Archives (.zip, .tar, .gz, .7z, .rar)
        if header.startswith(b"PK\x03\x04") or ext in ['.zip', '.tar', '.gz', '.tgz', '.7z', '.rar']:
            return self.archive_scanner.scan(filepath)

        # 4. Scripts (.py, .ps1, .bat, .vbs, .js, .cmd)
        if ext in ['.py', '.ps1', '.bat', '.vbs', '.js', '.cmd', '.sh']:
            return self.script_scanner.scan(filepath)

        # 5. Documents (.pdf, .docx, .xlsx, .pptx)
        if ext in ['.pdf', '.docx', '.xlsx', '.doc', '.xls']:
            return self.doc_scanner.scan(filepath)

        # 6. Default fallback for unknown files
        return True, "Passed basic scan"
