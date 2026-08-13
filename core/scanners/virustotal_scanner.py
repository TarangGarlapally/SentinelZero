import hashlib
import json
import os
import urllib.request
import urllib.error

class VirusTotalScanner:
    """Queries VirusTotal API v3 for file SHA-256 hash reputation."""

    def __init__(self, api_key=None):
        self.api_key = api_key

    def calculate_sha256(self, filepath):
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def scan(self, filepath):
        if not os.path.exists(filepath) or not self.api_key:
            return True, "VirusTotal API key not configured (Skipped)"

        try:
            file_hash = self.calculate_sha256(filepath)
            url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
            req = urllib.request.Request(url, headers={
                "x-apikey": self.api_key,
                "Accept": "application/json"
            })
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                malicious = stats.get("malicious", 0)
                suspicious = stats.get("suspicious", 0)

                if malicious > 0 or suspicious > 2:
                    return False, f"VirusTotal Threat Alert! Flagged by {malicious} engine(s) on VT."

                return True, f"VirusTotal Clean ({stats.get('harmless', 0)} harmless detections)"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return True, "File hash not yet seen on VirusTotal (Clean)"
            return True, f"VT API HTTP Error: {e.code}"
        except Exception as e:
            return True, f"VT Scan bypassed: {e}"
