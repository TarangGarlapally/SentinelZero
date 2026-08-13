# Sentinel Zero - Proactive System Guard

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-blue.svg)](https://microsoft.com)
[![Build Status](https://img.shields.io/badge/Build-Passing-success.svg)]()

**Sentinel Zero** is an autonomous, real-time security suite designed to proactively block zero-day infostealers, malicious 3D asset scripts, and browser credential harvest attacks. 

Unlike traditional reactive antivirus scanners, **Sentinel Zero** places an **instant Windows API Exclusive Lock (`FILE_SHARE_NONE`)** on any file downloaded or created across all browsers and directories *before* any application or user process can open or execute it.

---

## Key Features

* 🔒 **Universal Real-Time File Locking**: Intercepts file creation across all browsers (Chrome, Edge, Brave, Firefox) and applies native Windows API locks (`0` share mode). No application can touch or execute the file while scanning is active (scan time: 50ms – 400ms).
* 🎨 **3D Asset & `.blend` Script Inspector**: Parses Blender `.blend` binary structures (`DNA1` / `TXT` blocks) directly in memory, detecting embedded auto-executing Python payloads (`urllib`, `requests`, `exec()`, `base64`, C2 IP literals) before Blender ever touches the file.
* 📦 **Archive Payload Decompressor**: Recursively unpacks `.zip`, `.rar`, `.7z`, `.tar`, and `.iso` archives in memory to detect disguised executables, hidden scripts, double extensions (e.g. `invoice.pdf.exe`), and fake `Blender.exe` runtimes.
* 🛡️ **Browser Cookie Vault Guard**: Continuously monitors Chrome, Edge, Brave, and Firefox `Cookies` database files and immediately terminates any non-browser process attempting to harvest session tokens.
* ⚡ **Portable PE Executable Analyzer**: Evaluates Shannon entropy on `.exe` / `.dll` files to flag packed stealers (Lumma, Stealc, Vidar) and audits API import tables for credential harvesting calls (`CryptUnprotectData`, `sqlite3_open`).
* 🖥️ **Windows Boot Autostart & Tray UI**: Runs silently in the Windows System Tray with dark-mode styling, native toast notifications, and automatic Windows startup via Registry integration.

---

## Architecture Overview

```
                          [ Download / File Created ]
                                      │
                                      ▼
                      ┌───────────────────────────────┐
                      │  Windows API Exclusive Lock   │
                      │      (FILE_SHARE_NONE)        │
                      └───────────────┬───────────────┘
                                      │
                                      ▼
                      ┌───────────────────────────────┐
                      │    Universal Threat Router    │
                      └───────────────┬───────────────┘
                                      │
         ┌──────────────────┬─────────┴─────────┬──────────────────┐
         ▼                  ▼                   ▼                  ▼
  [ PE Scanner ]   [ Archive Scanner ]   [ Blend Scanner ]   [ Script Scanner ]
  - Entropy        - Double Extension    - DNA1/TXT Blocks   - AST Heuristics
  - Stealer APIs   - Disguised Exes      - Net / Exec Calls  - C2 IP Literals
         │                  │                   │                  │
         └──────────────────┴─────────┬─────────┴──────────────────┘
                                      │
                        ┌─────────────┴─────────────┐
                        ▼                           ▼
               [ Clean File ]              [ Threat Detected ]
             - Release Lock              - Lock Maintained
             - Safe Toast Alert          - Move to Quarantine
                                         - Threat Toast Alert
```

---

## Installation & Setup

### Prerequisites
* Windows 10 or 11 (x64)
* Python 3.10 or higher

### Quick Start
```bash
# 1. Clone the repository
git clone https://github.com/TarangGarlapally/SentinelZero.git
cd SentinelZero

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create configuration from template
copy config.example.json config.json

# 4. Run Sentinel Zero
python app.py
```

---

## Project Structure

```
SentinelZero/
├── app.py                      # Main daemon launcher & background service
├── config.json                 # Active user configuration
├── config.example.json         # Template configuration file
├── requirements.txt            # Python dependencies
├── core/
│   ├── watchdog_engine.py       # Universal real-time filesystem monitor
│   ├── file_locker.py           # Windows API exclusive lock & quarantine vault
│   ├── cookie_guard.py          # Browser cookie access watchdog & PID blocker
│   └── scanners/
│       ├── universal_scanner.py # Main threat router for ANY file extension
│       ├── archive_scanner.py   # Recursive archive inspector (.zip, .rar, .7z)
│       ├── pe_scanner.py        # Executable binary analyzer (Entropy & Imports)
│       ├── script_scanner.py    # Multi-language static analyzer (.py, .ps1, .bat)
│       ├── blend_scanner.py     # Blender .blend embedded script parser
│       └── doc_scanner.py       # Document macro & PDF exploit inspector
├── gui/
│   ├── tray_gui.py             # System Tray UI & Windows Toast notification manager
│   └── quarantine_window.py    # Dark-mode Quarantine Vault GUI
├── utils/
│   ├── autostart.py            # Windows Boot autostart manager
│   └── logger.py               # Security audit logging engine
└── Quarantine/                 # Isolated vault for blocked threats
```

---

## Testing & Verification

Run the built-in automated test suite to verify file locking, script detection, and registry autostart:

```bash
python test_verification.py
```

---

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
