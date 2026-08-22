import os
import time
from .blend_scanner import BlendScanner
from .pe_scanner import PEScanner
from .script_scanner import ScriptScanner
from .archive_scanner import ArchiveScanner
from .doc_scanner import DocScanner
from .yara_scanner import SignatureScanner
from .virustotal_scanner import VirusTotalScanner

class UniversalScanner:
    """Universal threat router for ANY file type downloaded or created on the system."""

    def __init__(self, vt_api_key=None):
        self.blend_scanner = BlendScanner()
        self.pe_scanner = PEScanner()
        self.script_scanner = ScriptScanner()
        self.archive_scanner = ArchiveScanner()
        self.doc_scanner = DocScanner()
        self.signature_scanner = SignatureScanner()
        self.vt_scanner = VirusTotalScanner(api_key=vt_api_key)

    def _read_header_safe(self, filepath):
        """Reads file header with retry logic to allow browser flush to complete."""
        header = b""
        for _ in range(5):
            try:
                with open(filepath, "rb") as f:
                    header = f.read(16)
                    break
            except PermissionError:
                time.sleep(0.1)
            except Exception:
                break
        return header

    def scan_file(self, filepath):
        if not os.path.exists(filepath):
            return True, "File no longer exists"

        # 1. Run Signature Rule Scan (Stealc, Lumma, RedLine, Raccoon signatures)
        sig_clean, sig_msg = self.signature_scanner.scan(filepath)
        if not sig_clean:
            return False, sig_msg

        # 2. Run VirusTotal Hash API Scan (if key configured)
        vt_clean, vt_msg = self.vt_scanner.scan(filepath)
        if not vt_clean:
            return False, vt_msg

        # 3. Read header safely with retry
        ext = os.path.splitext(filepath)[1].lower()
        header = self._read_header_safe(filepath)

        if header.startswith(b"MZ") or ext in ['.exe', '.dll', '.msi', '.scr', '.sys']:
            return self.pe_scanner.scan(filepath)

        if header.startswith(b"BLENDER") or ext == '.blend':
            return self.blend_scanner.scan(filepath)

        if header.startswith(b"PK\x03\x04") or ext in ['.zip', '.tar', '.gz', '.tgz', '.7z', '.rar']:
            return self.archive_scanner.scan(filepath)

        if ext in ['.py', '.ps1', '.bat', '.vbs', '.js', '.cmd', '.sh']:
            return self.script_scanner.scan(filepath)

        if ext in ['.pdf', '.docx', '.xlsx', '.doc', '.xls']:
            return self.doc_scanner.scan(filepath)

        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mkv', '.mp3']:
            return True, "✓ Clean Image / Media File"

        return True, "✓ Passed all security checks"
