import http.server
import socketserver
import threading
import json
import os
from core.scan_history import scan_history

DEFAULT_PORT = 9090
DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "SentinelZero")
HISTORY_FILE_PATH = os.path.join(DATA_DIR, "scan_history.json")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sentinel Zero - Security Protection Dashboard</title>
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
        .badge-safe { background: #166534; color: #4ade80; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 12px; }
        .badge-threat { background: #991b1b; color: #f87171; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 12px; }
        .filter-btn { background: #334155; color: #f8fafc; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; margin-right: 8px; }
        .filter-btn.active { background: #0284c7; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Sentinel Zero - Universal Protection Dashboard</h1>
        <span class="badge">SYSTEM PROTECTED & ACTIVE</span>
    </div>

    <div class="grid">
        <div class="card">
            <h3>Total Files Verified</h3>
            <div class="stat" id="stat-scanned">0</div>
            <p>Locked & verified clean before execution</p>
        </div>
        <div class="card">
            <h3>Clean & Successful Scans</h3>
            <div class="stat status-ok" id="stat-safe">0</div>
            <p>Unlocked & verified safe</p>
        </div>
        <div class="card">
            <h3>Quarantined Threats</h3>
            <div class="stat" style="color:#f87171;" id="stat-threats">0</div>
            <p>Blocked & quarantined</p>
        </div>
    </div>

    <div class="card" style="margin-top: 25px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h3>📋 Download Inspection History & Scan Logs</h3>
            <div>
                <button class="filter-btn active" id="filter-all" onclick="setFilter('ALL')">All Scans</button>
                <button class="filter-btn" id="filter-safe" onclick="setFilter('SAFE')">Clean Scans Only</button>
                <button class="filter-btn" id="filter-threat" onclick="setFilter('QUARANTINED')">Threats Only</button>
            </div>
        </div>
        <table>
            <thead>
                <tr>
                    <th>File Name</th>
                    <th>Downloaded Path</th>
                    <th>Status</th>
                    <th>Scan Findings / Verification</th>
                    <th>Timestamp</th>
                </tr>
            </thead>
            <tbody id="history-table">
                <tr><td colspan="5">Loading inspection history...</td></tr>
            </tbody>
        </table>
    </div>

    <script>
        let currentFilter = 'ALL';
        let rawHistory = [];

        function setFilter(filter) {
            currentFilter = filter;
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            if (filter === 'ALL') document.getElementById('filter-all').classList.add('active');
            if (filter === 'SAFE') document.getElementById('filter-safe').classList.add('active');
            if (filter === 'QUARANTINED') document.getElementById('filter-threat').classList.add('active');
            renderTable();
        }

        function renderTable() {
            const tbody = document.getElementById('history-table');
            let filtered = rawHistory;
            if (currentFilter === 'SAFE') filtered = rawHistory.filter(h => h.status === 'SAFE');
            if (currentFilter === 'QUARANTINED') filtered = rawHistory.filter(h => h.status === 'QUARANTINED');

            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:20px; color:#94a3b8;">No matching files found in this view.</td></tr>';
                return;
            }

            tbody.innerHTML = filtered.map(item => `
                <tr>
                    <td style="font-weight:bold; color:${item.status === 'SAFE' ? '#f8fafc' : '#f87171'};">${item.filename}</td>
                    <td style="color:#94a3b8; font-family:monospace; font-size:12px;">${item.filepath}</td>
                    <td>
                        <span class="${item.status === 'SAFE' ? 'badge-safe' : 'badge-threat'}">
                            ${item.status === 'SAFE' ? '✓ SAFE' : '🚨 QUARANTINED'}
                        </span>
                    </td>
                    <td>${item.finding}</td>
                    <td style="color:#94a3b8; font-size:12px;">${new Date(item.timestamp * 1000).toLocaleTimeString()}</td>
                </tr>
            `).join('');
        }

        async function loadHistory() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                
                rawHistory = data.history || [];
                const totalCount = data.scanned_count || rawHistory.length;
                document.getElementById('stat-scanned').innerText = totalCount;
                
                const safeCount = rawHistory.filter(h => h.status === 'SAFE').length;
                const threatCount = rawHistory.filter(h => h.status === 'QUARANTINED').length;
                
                document.getElementById('stat-safe').innerText = safeCount;
                document.getElementById('stat-threats').innerText = threatCount;
                
                renderTable();
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
            
            if os.path.exists(HISTORY_FILE_PATH):
                try:
                    with open(HISTORY_FILE_PATH, "r", encoding="utf-8") as f:
                        content = f.read()
                        self.wfile.write(content.encode('utf-8'))
                        return
                except Exception as e:
                    print(f"[WebDashboard] Error reading history file: {e}")

            stats = scan_history.get_stats()
            self.wfile.write(json.dumps(stats).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress HTTP logging

def start_dashboard_server(port=DEFAULT_PORT):
    for p in [port, 9090, 9091, 9092]:
        try:
            server = socketserver.TCPServer(("127.0.0.1", p), DashboardRequestHandler)
            print(f"[WebDashboard] Running live at http://localhost:{p}")
            server.serve_forever()
            break
        except Exception:
            continue

def run_dashboard_bg(port=DEFAULT_PORT):
    t = threading.Thread(target=start_dashboard_server, args=(port,), daemon=True)
    t.start()
    return t
