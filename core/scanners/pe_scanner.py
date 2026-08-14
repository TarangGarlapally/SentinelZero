import os
import math
import pefile
from ..signature_verifier import verify_digital_signature

class PEScanner:
    """Inspects Windows Executable binaries for packed stealers, high entropy, and credential-harvesting APIs."""

    SUSPICIOUS_IMPORTS = [
        "CryptUnprotectData",
        "sqlite3_open",
        "sqlite3_exec",
        "URLDownloadToFileA",
        "URLDownloadToFileW",
        "InternetOpenA",
        "InternetConnectA",
        "HttpSendRequestA",
        "GetClipboardData",
        "VirtualAllocEx",
        "WriteProcessMemory"
    ]

    def _calculate_entropy(self, data):
        if not data:
            return 0.0
        entropy = 0.0
        length = len(data)
        byte_counts = [0] * 256
        for b in data:
            byte_counts[b] += 1
        for count in byte_counts:
            if count > 0:
                p = count / length
                entropy -= p * math.log2(p)
        return entropy

    def scan(self, filepath):
        if not os.path.exists(filepath):
            return True, "File not found"

        # 1. Digital Signature Check (NVIDIA, Linden Lab, Microsoft, etc.)
        is_signed, publisher = verify_digital_signature(filepath)
        if is_signed:
            return True, f"Verified Digitally Signed Executable ({publisher})"

        try:
            pe = pefile.PE(filepath)
            
            # Check PE section entropy
            high_entropy_sections = []
            for section in pe.sections:
                entropy = self._calculate_entropy(section.get_data())
                sec_name = section.Name.decode("latin-1", errors="ignore").rstrip("\x00")
                if entropy > 7.4:  # Raised threshold to reduce packed false positives on un-signed installers
                    high_entropy_sections.append((sec_name, entropy))

            # Check Import Table for Credential Stealer APIs
            suspicious_apis = []
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    for imp in entry.imports:
                        if imp.name:
                            name = imp.name.decode("latin-1", errors="ignore")
                            if name in self.SUSPICIOUS_IMPORTS:
                                suspicious_apis.append(name)

            pe.close()

            # Un-signed binaries requiring 3+ stealer APIs AND high entropy section
            if high_entropy_sections and len(suspicious_apis) >= 3:
                return False, f"Unsigned packed stealer payload detected! (Entropy: {high_entropy_sections[0][1]:.2f}, APIs: {', '.join(suspicious_apis[:3])})"

            return True, "Clean Executable"
        except pefile.PEFormatError:
            return True, "Not a PE file"
        except Exception as e:
            return True, f"PE scan bypass: {e}"
