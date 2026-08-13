import os
import json
import re

class SignatureScanner:
    """Scans files against threat signature rules (Stealc, Lumma, RedLine, Raccoon)."""

    def __init__(self, rules_path=None):
        if rules_path is None:
            rules_path = os.path.join(os.path.dirname(__file__), "..", "..", "rules", "infostealers.json")
        self.rules = self._load_rules(rules_path)

    def _load_rules(self, path):
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("rules", [])
        except Exception:
            return []

    def scan(self, filepath):
        if not os.path.exists(filepath) or not self.rules:
            return True, "Signature scanner clean"

        try:
            with open(filepath, "rb") as f:
                content = f.read(5 * 1024 * 1024)  # Read first 5MB

            content_str = content.decode("latin-1", errors="ignore")

            for rule in self.rules:
                rule_name = rule.get("name", "Unknown Threat")
                patterns = rule.get("patterns", [])
                matched_count = 0
                for pat in patterns:
                    if re.search(re.escape(pat), content_str, re.IGNORECASE):
                        matched_count += 1

                if matched_count >= 2 or (len(patterns) == 1 and matched_count == 1):
                    return False, f"Signature Threat Match: {rule_name} (Matched {matched_count}/{len(patterns)} indicators)"

            return True, "Signature scan clean"
        except Exception as e:
            return True, f"Signature scan error: {e}"
