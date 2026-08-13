# Sentinel Zero - Proactive System Guard v1.1.0

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-blue.svg)](https://microsoft.com)
[![Build Status](https://img.shields.io/badge/Build-Passing-success.svg)]()

**Sentinel Zero** is an autonomous, real-time security suite designed to proactively block zero-day infostealers, credential harvest attacks, and malicious downloads across all file types.

Unlike traditional reactive antivirus scanners that analyze files *after* they are written to disk, **Sentinel Zero** places an **instant Windows API Exclusive Lock (`FILE_SHARE_NONE`)** on any file downloaded or created across all web browsers and directories *before* any application, background script, or user process can open or execute it.

---

## Universal Protection Engine (ALL File Types)

Sentinel Zero protects your system against threats across **every file category**:

* 🔒 **Universal Real-Time File Locking**: Intercepts file creation across all browsers (Chrome, Edge, Brave, Firefox, Opera) and applies native Windows API locks (`0` share mode). No application can touch or execute the file while scanning is active (scan time: 50ms – 400ms).
* 🎯 **Infostealer Signature Engine**: Scans files against threat rules (`rules/infostealers.json`) targeting major stealer families (**Stealc, Lumma, RedLine, Raccoon, Vidar, Rhadamanthys, MetaStealer**).
* 📦 **Compressed Archive Recursive Inspector**: Unpacks `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, and `.iso` archives in memory to detect disguised executables, hidden payload scripts, double extensions (e.g. `invoice.pdf.exe`), and embedded runtimes.
* ⚡ **PE Executable & Binary Analyzer**: Evaluates Shannon entropy on `.exe`, `.msi`, `.dll`, and `.scr` files to catch packed/encrypted malware and audits API import tables for credential-harvesting functions (`CryptUnprotectData`, `sqlite3_open`).
* 📜 **Multi-Language Script Static Analyzer**: Heuristic AST parser for `.py`, `.ps1`, `.bat`, `.vbs`, `.js`, and `.cmd` scripts targeting remote downloader calls (`urllib`, `requests`, `Invoke-WebRequest`, `WScript.Shell`), obfuscated Base64, and C2 IP literals.
* 📄 **Document Exploit Inspector**: Audits `.pdf`, `.docx`, `.xlsx`, and `.pptx` streams for suspicious OLE VBA macros and auto-executing triggers.
* 🎨 **3D Asset & Project File Parser**: Parses `.blend`, `.fbx`, and `.gltf` binary streams directly in memory to detect embedded auto-running scripts before host applications open them.
* 🛡️ **Browser Cookie Vault Guard**: Continuously monitors Chrome, Edge, Brave, and Firefox `Cookies` database files and immediately terminates any non-browser process attempting to harvest session tokens.
* 🌐 **VirusTotal Hash Reputation API**: Optional VirusTotal API v3 integration to instantly verify SHA-256 hashes against 70+ antivirus engines.
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
[ PE Scanner ]  [ Archive ]       [ Script Scanner] [ Doc / 3D ]     [ Signature Rules ]
- Entropy       - Double Ext     - AST Heuristics   - OLE Macros     - Stealc / Lumma
- Stealer APIs  - Disguised Exes - Net/Exec Calls   - Embedded Code  - RedLine / Raccoon
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

# Scan any file or directory
python cli.py scan C:\path\to\file_or_folder

# Enable/Disable Windows Boot Autostart
python cli.py autostart enable
```

---

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
