import http.server
import socketserver
import threading
import json
import os
from core.scan_history import scan_history

PORT = 9090
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sentinel Zero - Security Threat Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 15px; }
        .header h1 { margin: 0; color: #38bdf8; font-size: 24px; }
        .badge { background: #166534; color: #4ade80; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: bold; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 20px; }
        .card { background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }
        .card h3 { margin-top: 0; color: #94a3b8; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }
        .stat { font-size: 36px; font-weight: bold; color: #38bdf8; margin: 10px 0; }
        .status-ok { color: #4ade80; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; font-size: 14px; }
        th { color: #94a3b8; font-weight: 600; text-transform: uppercase; font-size: 12px; }
        .badge-threat { background: #991b1b; color: #f87171; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Sentinel Zero - Real-Time Threat Guard</h1>
        <span class="badge">SYSTEM PROTECTED & ACTIVE</span>
    </div>

    <div class="grid">
        <div class="card">
            <h3>Total Downloads Verified</h3>
            <div class="stat" id="stat-scanned">0</div>
            <p>Clean downloads pass silently</p>
        </div>
        <div class="card">
            <h3>System Status</h3>
            <div class="stat status-ok">SECURE</div>
            <p>0 Active Infostealer Threats</p>
        </div>
        <div class="card">
            <h3>Blocked Threats</h3>
            <div class="stat" style="color:#f87171;" id="stat-threats">0</div>
            <p>Blocked & Quarantined</p>
        </div>
    </div>

    <div class="card" style="margin-top: 25px;">
        <h3>🚨 Blocked Threat Incident Log</h3>
        <table>
            <thead>
                <tr>
                    <th>Threat Name</th>
                    <th>Intercepted Path</th>
                    <th>Status</th>
                    <th>Threat Reason / Detection</th>
                    <th>Timestamp</th>
                </tr>
            </thead>
            <tbody id="history-table">
                <tr><td colspan="5">Loading threat incidents...</td></tr>
            </tbody>
        </table>
    </div>

    <script>
        async function loadHistory() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                
                document.getElementById('stat-scanned').innerText = data.scanned_count || 0;
                
                const history = (data.history || []).filter(h => h.status === 'QUARANTINED');
                document.getElementById('stat-threats').innerText = history.length;
                
                const tbody = document.getElementById('history-table');
                if (history.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" style="color:#4ade80; text-align:center; padding:20px;">✅ Zero Threats Detected. Genuine downloads pass silently without log clutter.</td></tr>';
                    return;
                }
                
                tbody.innerHTML = history.map(item => `
                    <tr>
                        <td style="font-weight:bold; color:#f87171;">${item.filename}</td>
                        <td style="color:#94a3b8; font-family:monospace; font-size:12px;">${item.filepath}</td>
                        <td>
                            <span class="badge-threat">🚨 BLOCKED & QUARANTINED</span>
                        </td>
                        <td>${item.finding}</td>
                        <td style="color:#94a3b8; font-size:12px;">${new Date(item.timestamp * 1000).toLocaleTimeString()}</td>
                    </tr>
                `).join('');
            } catch(e) {}
        }
        loadHistory();
        setInterval(loadHistory, 3000);
    </script>
</body>
</html>
"""

class DashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/', '/index.html']:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            stats = scan_history.get_stats()
            self.wfile.write(json.dumps(stats).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress HTTP logging

def start_dashboard_server(port=PORT):
    try:
        server = socketserver.TCPServer(("127.0.0.1", port), DashboardRequestHandler)
        print(f"[WebDashboard] Running live at http://localhost:{port}")
        server.serve_forever()
    except Exception as e:
        print(f"[WebDashboard] Could not start server: {e}")

def run_dashboard_bg(port=PORT):
    t = threading.Thread(target=start_dashboard_server, args=(port,), daemon=True)
    t.start()
    return t
