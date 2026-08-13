import os
import json
import urllib.request

DEFAULT_FEED_URL = "https://raw.githubusercontent.com/TarangGarlapally/SentinelZero/main/rules/infostealers.json"

class FeedUpdater:
    """Syncs the latest infostealer threat signatures & rules automatically."""

    def __init__(self, rules_file=None):
        if rules_file is None:
            rules_file = os.path.join(os.path.dirname(__file__), "..", "rules", "infostealers.json")
        self.rules_file = rules_file

    def update_rules(self):
        try:
            req = urllib.request.Request(DEFAULT_FEED_URL, headers={"User-Agent": "SentinelZero-Updater/1.2.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read().decode('utf-8')
                data = json.loads(content)
                
                # Validate JSON structure
                if "rules" in data and isinstance(data["rules"], list):
                    os.makedirs(os.path.dirname(self.rules_file), exist_ok=True)
                    with open(self.rules_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    print(f"[FeedUpdater] Successfully updated {len(data['rules'])} threat rules.")
                    return True, f"Updated {len(data['rules'])} rules."
            return False, "Invalid feed format"
        except Exception as e:
            return False, f"Feed update skipped: {e}"
