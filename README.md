# Sentinel Zero - Proactive System Guard v1.1.0

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-blue.svg)](https://microsoft.com)
[![Build Status](https://img.shields.io/badge/Build-Passing-success.svg)]()

**Sentinel Zero** is an autonomous, real-time security suite designed to proactively block zero-day infostealers, malicious 3D asset scripts, and browser credential harvest attacks. 

Unlike traditional reactive antivirus scanners, **Sentinel Zero** places an **instant Windows API Exclusive Lock (`FILE_SHARE_NONE`)** on any file downloaded or created across all browsers and directories *before* any application or user process can open or execute it.

---

## Key Features in v1.1.0

* 🔒 **Universal Real-Time File Locking**: Intercepts file creation across all browsers (Chrome, Edge, Brave, Firefox) and applies native Windows API locks (`0` share mode). No application can touch or execute the file while scanning is active (scan time: 50ms – 400ms).
* 🎯 **Signature Threat Engine**: Scans files against threat rules (`rules/infostealers.json`) for known infostealers (**Stealc, Lumma, RedLine, Raccoon, Vidar, Rhadamanthys**).
* 🌐 **VirusTotal Hash Reputation API**: Optional VirusTotal API v3 integration to instantly verify SHA-256 hashes against 70+ antivirus engines.
* 🎨 **3D Asset & `.blend` Script Inspector**: Parses Blender `.blend` binary structures (`DNA1` / `TXT` blocks) directly in memory, detecting embedded auto-executing Python payloads (`urllib`, `requests`, `exec()`, `base64`, C2 IP literals) before Blender ever touches the file.
* 📦 **Archive Payload Decompressor**: Recursively unpacks `.zip`, `.rar`, `.7z`, `.tar`, and `.iso` archives in memory to detect disguised executables, hidden scripts, double extensions (e.g. `invoice.pdf.exe`), and fake `Blender.exe` runtimes.
* 🛡️ **Browser Cookie Vault Guard**: Continuously monitors Chrome, Edge, Brave, and Firefox `Cookies` database files and immediately terminates any non-browser process attempting to harvest session tokens.
* ⚡ **Portable PE Executable Analyzer**: Evaluates Shannon entropy on `.exe` / `.dll` files to flag packed stealers and audits API import tables for credential harvesting calls (`CryptUnprotectData`, `sqlite3_open`).
* 💻 **CLI Control Center**: Command Line Interface for quick system diagnostics, folder scanning, and autostart management (`python cli.py status`).
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
  ┌─────────────────┬─────────────────┼─────────────────┬─────────────────┐
  ▼                 ▼                 ▼                 ▼                 ▼
[ PE Scanner ]  [ Archive ]      [ Blend Scanner ] [ Script Scanner ] [ Signature Rules ]
- Entropy       - Double Ext     - DNA1/TXT Blocks - AST Heuristics   - Stealc / Lumma
- Stealer APIs  - Disguised Exes - Net/Exec Calls  - C2 IP Literals   - RedLine / Raccoon
  │                 │                 │                 │                 │
  └─────────────────┴─────────────────┼─────────────────┴─────────────────┘
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

### CLI Control Center
```bash
# Check protection status
python cli.py status

# Scan a file or directory
python cli.py scan C:\path\to\file_or_folder

# Enable/Disable Windows Boot Autostart
python cli.py autostart enable
```

---

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
