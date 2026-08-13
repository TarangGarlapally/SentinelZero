# Sentinel Zero - Proactive System Guard v1.3.0

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-blue.svg)](https://microsoft.com)
[![Build Status](https://img.shields.io/badge/Build-Passing-success.svg)]()

**Sentinel Zero** is an autonomous, real-time security suite designed to proactively block zero-day infostealers, credential harvest attacks, and malicious downloads across all file types.

Unlike traditional reactive antivirus scanners that analyze files *after* they are written to disk, **Sentinel Zero** places an **instant Windows API Exclusive Lock (`FILE_SHARE_NONE`)** on any file downloaded across all web browsers and directories *before* any application, background script, or user process can open or execute it.

---

## Downloads & Installation

### Option 1: Standalone Windows App (No Python Required)
1. Download **`SentinelZero-Setup.exe`** (32.6 MB) from the [Releases](https://github.com/TarangGarlapally/SentinelZero/releases) page or from `dist/SentinelZero-Setup.exe`.
2. Double-click **`SentinelZero-Setup.exe`** to run Sentinel Zero directly as a native Windows GUI app.
3. Sentinel Zero runs silently in your System Tray and opens the Web Security Dashboard at **`http://localhost:9090`**.

### Option 2: Run from Source / Python
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

### Build Your Own Standalone Executable
```bash
python build_installer.py
# Output generated in dist/SentinelZero-Setup.exe
```

---

## Universal Protection Engine (ALL File Types)

* 🌐 **Browser Download Interceptor (ANY Folder & Drive)**: Monitors **ANY folder** on your PC (`Downloads`, `Desktop`, `Projects`, `Documents`, custom drives), but **ONLY triggers when an actual web browser download completes** (detecting `.crdownload`, `.part`, `.tmp` $\rightarrow$ final file renames or Windows Zone.Identifier Mark-of-the-Web). *Ignores IDE builds, code edits, and local file saves completely!*
* 📊 **Web Security Dashboard (`http://localhost:9090`)**: Local web interface displaying real-time protection statistics, live download interception logs (showing safe files & threats with exact scan findings), and an interactive Vault manager.
* 🔒 **Universal Real-Time File Locking**: Intercepts completed downloads across all browsers (Chrome, Edge, Brave, Firefox, Opera) and applies native Windows API locks (`0` share mode). No application can touch or execute the file while scanning is active (scan time: 50ms – 400ms).
* 🎯 **Infostealer Signature Engine**: Scans files against threat rules (`rules/infostealers.json`) targeting major stealer families (**Stealc, Lumma, RedLine, Raccoon, Vidar, Rhadamanthys, MetaStealer**).
* 📦 **Compressed Archive Recursive Inspector**: Unpacks `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, and `.iso` archives in memory to detect disguised executables, hidden payload scripts, double extensions (e.g. `invoice.pdf.exe`), and embedded runtimes.
* ⚡ **PE Executable & Binary Analyzer**: Evaluates Shannon entropy on `.exe`, `.msi`, `.dll`, and `.scr` files to catch packed/encrypted malware and audits API import tables for credential-harvesting functions (`CryptUnprotectData`, `sqlite3_open`).
* 📜 **Multi-Language Script Static Analyzer**: Heuristic AST parser for `.py`, `.ps1`, `.bat`, `.vbs`, and `.js` scripts targeting remote downloader calls (`urllib`, `requests`, `Invoke-WebRequest`, `WScript.Shell`), obfuscated Base64, and C2 IP literals.
* 🛡️ **Browser Cookie Vault Guard**: Continuously monitors Chrome, Edge, Brave, and Firefox `Cookies` database files and immediately terminates any non-browser process attempting to harvest session tokens.
* 💻 **CLI Control Center**: Command Line Interface for quick system diagnostics, folder scanning, and autostart management (`python cli.py status`).

---

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
