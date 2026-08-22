import http.server
import socketserver
import threading
import json
import os
from core.scan_history import scan_history

DEFAULT_PORT = 9090
DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "SentinelZero")
HISTORY_FILE_PATH = os.path.join(DATA_DIR, "scan_history.json")
CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

ON_CONFIG_UPDATED_CALLBACK = None

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
        .save-btn { background: #0284c7; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; margin-top: 15px; }
        .save-btn:hover { background: #0369a1; }
        .form-group { margin-bottom: 15px; }
        .checkbox-group { display: flex; flex-direction: column; gap: 8px; margin-top: 8px; }
        .checkbox-label { display: flex; align-items: center; gap: 8px; font-size: 14px; cursor: pointer; }
        .input-text { width: 100%; max-width: 500px; padding: 8px 12px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 6px; font-family: monospace; }
        .toast-msg { background: #166534; color: #4ade80; padding: 10px; border-radius: 6px; margin-top: 10px; display: none; font-weight: bold; }
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

    <!-- Folder Monitoring Configuration Section -->
    <div class="card" style="margin-top: 25px;">
        <h3>⚙️ Folder Monitoring Configuration (Multi-Select)</h3>
        <p style="color: #94a3b8; font-size: 14px; margin-bottom: 15px;">Choose whether to monitor your entire user profile or multi-select specific folders to watch for web downloads.</p>
        
        <div class="form-group">
            <label class="checkbox-label" style="font-weight: bold; font-size: 15px;">
                <input type="radio" name="watch_mode" value="ALL" id="mode-all" onchange="toggleMode()">
                🌐 Monitor All System Folders (C:\\Users\\taran)
            </label>
        </div>

        <div class="form-group">
            <label class="checkbox-label" style="font-weight: bold; font-size: 15px;">
                <input type="radio" name="watch_mode" value="CUSTOM" id="mode-custom" onchange="toggleMode()">
                📁 Choose Specific Folders (Multi-Select)
            </label>
        </div>

        <div id="custom-folders-panel" style="margin-left: 25px; padding-left: 15px; border-left: 2px solid #334155; display: none;">
            <div class="checkbox-group">
                <label class="checkbox-label">
                    <input type="checkbox" class="custom-dir-check" value="C:\\Users\\taran\\Downloads"> Downloads Folder (<code style="color:#38bdf8;">C:\\Users\\taran\\Downloads</code>)
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" class="custom-dir-check" value="C:\\Users\\taran\\Desktop"> Desktop Folder (<code style="color:#38bdf8;">C:\\Users\\taran\\Desktop</code>)
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" class="custom-dir-check" value="C:\\Users\\taran\\Documents"> Documents Folder (<code style="color:#38bdf8;">C:\\Users\\taran\\Documents</code>)
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" class="custom-dir-check" value="C:\\Users\\taran\\Pictures"> Pictures Folder (<code style="color:#38bdf8;">C:\\Users\\taran\\Pictures</code>)
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" class="custom-dir-check" value="C:\\Users\\taran\\Videos"> Videos Folder (<code style="color:#38bdf8;">C:\\Users\\taran\\Videos</code>)
                </label>
            </div>
            
            <div style="margin-top: 15px;">
                <label style="font-size: 13px; color: #94a3b8;">Additional Custom Folder Paths (comma-separated):</label><br>
                <input type="text" id="extra-custom-paths" class="input-text" placeholder="e.g. C:\\Games, D:\\Downloads" style="margin-top: 5px;">
            </div>
        </div>

        <button class="save-btn" onclick="saveFolderConfig()">💾 Save Folder Monitoring Settings</button>
        <div class="toast-msg" id="save-toast">✓ Folder Monitoring Configuration Saved & Active!</div>
    </div>

    <!-- History Table -->
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

        function toggleMode() {
            const isCustom = document.getElementById('mode-custom').checked;
            document.getElementById('custom-folders-panel').style.display = isCustom ? 'block' : 'none';
        }

        async function loadConfig() {
            try {
                const res = await fetch('/api/config');
                const config = await res.json();
                
                const mode = config.watch_mode || "ALL";
                if (mode === "ALL") {
                    document.getElementById('mode-all').checked = true;
                } else {
                    document.getElementById('mode-custom').checked = true;
                }
                toggleMode();

                const customDirs = config.custom_watch_directories || ["C:\\\\Users\\\\taran\\\\Downloads", "C:\\\\Users\\\\taran\\\\Desktop", "C:\\\\Users\\\\taran\\\\Documents"];
                document.querySelectorAll('.custom-dir-check').forEach(chk => {
                    chk.checked = customDirs.includes(chk.value);
                });

                const standardPaths = ["C:\\\\Users\\\\taran\\\\Downloads", "C:\\\\Users\\\\taran\\\\Desktop", "C:\\\\Users\\\\taran\\\\Documents", "C:\\\\Users\\\\taran\\\\Pictures", "C:\\\\Users\\\\taran\\\\Videos"];
                const extraDirs = customDirs.filter(d => !standardPaths.includes(d));
                document.getElementById('extra-custom-paths').value = extraDirs.join(', ');
            } catch(e) {}
        }

        async function saveFolderConfig() {
            const modeAll = document.getElementById('mode-all').checked;
            const watchMode = modeAll ? "ALL" : "CUSTOM";
            
            let selectedDirs = [];
            document.querySelectorAll('.custom-dir-check:checked').forEach(chk => {
                selectedDirs.push(chk.value);
            });

            const extraInput = document.getElementById('extra-custom-paths').value;
            if (extraInput.trim()) {
                const extras = extraInput.split(',').map(s => s.trim()).filter(s => s.length > 0);
                selectedDirs = selectedDirs.concat(extras);
            }

            const payload = {
                watch_mode: watchMode,
                custom_watch_directories: selectedDirs
            };

            try {
                const res = await fetch('/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                if (result.success) {
                    const toast = document.getElementById('save-toast');
                    toast.style.display = 'block';
                    setTimeout(() => toast.style.display = 'none', 4000);
                }
            } catch(e) {
                alert("Error saving configuration!");
            }
        }

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
        
        loadConfig();
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
        elif self.path == '/api/config':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if os.path.exists(CONFIG_FILE_PATH):
                with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(json.dumps({}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/config':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                # Update config.json
                current_config = {}
                if os.path.exists(CONFIG_FILE_PATH):
                    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                        current_config = json.load(f)
                
                watch_mode = data.get("watch_mode", "ALL")
                custom_dirs = data.get("custom_watch_directories", [])

                current_config["watch_mode"] = watch_mode
                current_config["custom_watch_directories"] = custom_dirs

                if watch_mode == "ALL":
                    current_config["watch_directories"] = ["C:\\Users\\taran"]
                else:
                    current_config["watch_directories"] = custom_dirs

                with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
                    json.dump(current_config, f, indent=2)

                if ON_CONFIG_UPDATED_CALLBACK:
                    ON_CONFIG_UPDATED_CALLBACK(current_config)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "config": current_config}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))

    def log_message(self, format, *args):
        pass  # Suppress HTTP logging

def set_config_updated_callback(callback):
    global ON_CONFIG_UPDATED_CALLBACK
    ON_CONFIG_UPDATED_CALLBACK = callback

def start_dashboard_server(port=DEFAULT_PORT):
    for p in [port, 9090, 9091, 9092]:
        try:
            server = socketserver.TCPServer(("127.0.0.1", p), DashboardRequestHandler)
            print(f"[WebDashboard] Running live at http://localhost:{p}")
            server.serve_forever()
            break
        except Exception:
            continue

def run_dashboard_bg(port=DEFAULT_PORT, on_config_updated=None):
    if on_config_updated:
        set_config_updated_callback(on_config_updated)
    t = threading.Thread(target=start_dashboard_server, args=(port,), daemon=True)
    t.start()
    return t
