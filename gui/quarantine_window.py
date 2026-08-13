import os
import json
import customtkinter as ctk
from core.scan_history import scan_history

class QuarantineWindow(ctk.CTk):
    """CustomTkinter GUI Vault & Download Activity Monitor."""

    def __init__(self, quarantine_dir):
        super().__init__()

        self.quarantine_dir = quarantine_dir
        self.title("Sentinel Zero - Download Security & Quarantine Manager")
        self.geometry("800x550")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Tabview navigation
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=15, pady=15, fill="both", expand=True)

        self.tab_history = self.tabview.add("📋 Download Activity & Findings")
        self.tab_vault = self.tabview.add("🛡️ Quarantine Vault")

        # Setup History Tab
        self.lbl_stats = ctk.CTkLabel(
            self.tab_history,
            text="Total Scanned Downloads: 0 | Safe: 0 | Threats: 0",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_stats.pack(padx=10, pady=10)

        self.frame_history_list = ctk.CTkScrollableFrame(self.tab_history, width=740, height=380)
        self.frame_history_list.pack(padx=10, pady=10, fill="both", expand=True)

        # Setup Vault Tab
        self.frame_vault_list = ctk.CTkScrollableFrame(self.tab_vault, width=740, height=420)
        self.frame_vault_list.pack(padx=10, pady=10, fill="both", expand=True)

        self.refresh_ui()

    def refresh_ui(self):
        self.refresh_history()
        self.refresh_vault()

    def refresh_history(self):
        for widget in self.frame_history_list.winfo_children():
            widget.destroy()

        stats = scan_history.get_stats()
        scanned_total = stats.get("scanned_count", 0)
        history = stats.get("history", [])

        safe_count = len([h for h in history if h.get("status") == "SAFE"])
        threat_count = len([h for h in history if h.get("status") == "QUARANTINED"])

        self.lbl_stats.configure(
            text=f"Total Downloads Scanned: {scanned_total} | Safe: {safe_count} | Threats Blocked: {threat_count}"
        )

        if not history:
            lbl = ctk.CTkLabel(self.frame_history_list, text="No download activity logged yet.", font=ctk.CTkFont(size=14))
            lbl.pack(pady=30)
            return

        for item in history:
            row = ctk.CTkFrame(self.frame_history_list)
            row.pack(padx=5, pady=4, fill="x", expand=True)

            status_symbol = "✓ SAFE" if item.get("status") == "SAFE" else "🚨 THREAT"
            status_color = "#4ade80" if item.get("status") == "SAFE" else "#f87171"

            lbl_txt = ctk.CTkLabel(
                row,
                text=f"[{status_symbol}]  {item.get('filename')}\nFinding: {item.get('finding')}\nPath: {item.get('filepath')}",
                justify="left",
                anchor="w",
                text_color=status_color,
                font=ctk.CTkFont(size=12)
            )
            lbl_txt.pack(side="left", padx=10, pady=8)

    def refresh_vault(self):
        for widget in self.frame_vault_list.winfo_children():
            widget.destroy()

        if not os.path.exists(self.quarantine_dir):
            return

        files = [f for f in os.listdir(self.quarantine_dir) if f.endswith(".json")]

        if not files:
            lbl = ctk.CTkLabel(self.frame_vault_list, text="Vault is Empty. No Threats Quarantined.", font=ctk.CTkFont(size=14))
            lbl.pack(pady=30)
            return

        for meta_file in files:
            meta_path = os.path.join(self.quarantine_dir, meta_file)
            quarantine_file = meta_path[:-5]

            try:
                with open(meta_path, "r") as f:
                    data = json.load(f)

                row_frame = ctk.CTkFrame(self.frame_vault_list)
                row_frame.pack(padx=10, pady=5, fill="x", expand=True)

                lbl_info = ctk.CTkLabel(
                    row_frame,
                    text=f"🚨 {os.path.basename(data.get('original_path', 'File'))}\nThreat: {data.get('threat', 'Unknown')}",
                    justify="left",
                    anchor="w"
                )
                lbl_info.pack(side="left", padx=10, pady=10)

                btn_del = ctk.CTkButton(
                    row_frame,
                    text="Delete",
                    fg_color="red",
                    width=80,
                    command=lambda p=quarantine_file, m=meta_path: self.delete_threat(p, m)
                )
                btn_del.pack(side="right", padx=10, pady=10)

            except Exception:
                pass

    def delete_threat(self, payload_path, meta_path):
        try:
            if os.path.exists(payload_path):
                os.remove(payload_path)
            if os.path.exists(meta_path):
                os.remove(meta_path)
        except Exception:
            pass
        self.refresh_ui()

if __name__ == "__main__":
    app = QuarantineWindow(r"C:\Users\taran\Projects\SentinelZero\Quarantine")
    app.mainloop()
