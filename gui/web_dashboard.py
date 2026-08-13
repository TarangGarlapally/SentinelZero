import http.server
import socketserver
import threading
import json
import os

PORT = 9090
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUARANTINE_DIR = os.path.join(BASE_DIR, "..", "Quarantine")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sentinel Zero - Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 15px; }
        .header h1 { margin: 0; color: #38bdf8; font-size: 24px; }
        .badge { background: #0284c7; color: white; padding: 4px 12px; borderRadius: 20px; font-size: 12px; font-weight: bold; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 20px; }
        .card { background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }
        .card h3 { margin-top: 0; color: #94a3b8; font-size: 14px; text-transform: uppercase; }
        .stat { font-size: 32px; font-weight: bold; color: #38bdf8; margin: 10px 0; }
        .status-ok { color: #4ade80; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #334155; font-size: 14px; }
        th { color: #94a3b8; font-weight: 600; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Sentinel Zero Security Dashboard</h1>
        <span class="badge">PROACTIVE LOCK ACTIVE</span>
    </div>

    <div class="grid">
        <div class="card">
            <h3>Protection Status</h3>
            <div class="stat status-ok">ACTIVE</div>
            <p>Universal Real-Time Lock & Cookie Vault Guard Running</p>
        </div>
        <div class="card">
            <h3>Files Intercepted</h3>
            <div class="stat" id="stat-scanned">AUTO</div>
            <p>Proactively locked and scanned prior to execution</p>
        </div>
        <div class="card">
            <h3>Quarantined Threats</h3>
            <div class="stat" style="color:#f87171;" id="stat-threats">0</div>
            <p>Isolated in Vault</p>
        </div>
    </div>

    <div class="card" style="margin-top: 20px;">
        <h3>Quarantine Vault Details</h3>
        <table>
            <thead>
                <tr>
                    <th>Original File Path</th>
                    <th>Threat Signature</th>
                    <th>Quarantine Time</th>
                </tr>
            </thead>
            <tbody id="vault-table">
                <tr><td colspan="3">Loading Vault...</td></tr>
            </tbody>
        </table>
    </div>

    <script>
        async function loadVault() {
            try {
                const res = await fetch('/api/vault');
                const data = await res.json();
                document.getElementById('stat-threats').innerText = data.length;
                const tbody = document.getElementById('vault-table');
                if (data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="3">Vault is empty. Zero threats quarantined.</td></tr>';
                    return;
                }
                tbody.innerHTML = data.map(item => `
                    <tr>
                        <td>${item.original_path || 'Unknown'}</td>
                        <td style="color:#f87171; font-weight:bold;">${item.threat || 'Malicious Payload'}</td>
                        <td>${new Date(item.quarantine_time * 1000).toLocaleString()}</td>
                    </tr>
                `).join('');
            } catch(e) {}
        }
        loadVault();
        setInterval(loadVault, 5000);
    </script>
</body>
</html>
"""

class DashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        elif self.path == '/api/vault':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            items = []
            if os.path.exists(QUARANTINE_DIR):
                for f in os.listdir(QUARANTINE_DIR):
                    if f.endswith(".json"):
                        try:
                            with open(os.path.join(QUARANTINE_DIR, f), "r") as json_f:
                                items.append(json.load(json_f))
                        except Exception:
                            pass
            self.wfile.write(json.dumps(items).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress HTTP access logging

def start_dashboard_server(port=PORT):
    try:
        server = socketserver.TCPServer(("127.0.0.1", port), DashboardRequestHandler)
        print(f"[WebDashboard] Server running at http://localhost:{port}")
        server.serve_forever()
    except Exception as e:
        print(f"[WebDashboard] Could not start server: {e}")

def run_dashboard_bg(port=PORT):
    t = threading.Thread(target=start_dashboard_server, args=(port,), daemon=True)
    t.start()
    return t

if __name__ == "__main__":
    start_dashboard_server()
