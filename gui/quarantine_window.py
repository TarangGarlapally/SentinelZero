import os
import json
import customtkinter as ctk

class QuarantineWindow(ctk.CTk):
    """CustomTkinter GUI Vault to inspect and manage quarantined threat files."""

    def __init__(self, quarantine_dir):
        super().__init__()

        self.quarantine_dir = quarantine_dir
        self.title("Sentinel Zero - Quarantine Vault")
        self.geometry("700x480")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Header Label
        self.label_header = ctk.CTkLabel(
            self, 
            text="🛡️ Sentinel Zero - Quarantined Threats", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.label_header.pack(padx=20, pady=15)

        # Quarantined listbox frame
        self.frame_list = ctk.CTkScrollableFrame(self, width=650, height=320)
        self.frame_list.pack(padx=20, pady=10, fill="both", expand=True)

        self.refresh_list()

    def refresh_list(self):
        # Clear existing items
        for widget in self.frame_list.winfo_children():
            widget.destroy()

        if not os.path.exists(self.quarantine_dir):
            return

        files = [f for f in os.listdir(self.quarantine_dir) if f.endswith(".json")]

        if not files:
            lbl = ctk.CTkLabel(self.frame_list, text="Vault is Empty. No Threats Quarantined.", font=ctk.CTkFont(size=14))
            lbl.pack(pady=30)
            return

        for meta_file in files:
            meta_path = os.path.join(self.quarantine_dir, meta_file)
            quarantine_file = meta_path[:-5]  # strip .json

            try:
                with open(meta_path, "r") as f:
                    data = json.load(f)

                row_frame = ctk.CTkFrame(self.frame_list)
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

            except Exception as e:
                pass

    def delete_threat(self, payload_path, meta_path):
        try:
            if os.path.exists(payload_path):
                os.remove(payload_path)
            if os.path.exists(meta_path):
                os.remove(meta_path)
        except Exception:
            pass
        self.refresh_list()

if __name__ == "__main__":
    app = QuarantineWindow(r"C:\Users\taran\.gemini\antigravity\scratch\SentinelZero\Quarantine")
    app.mainloop()
