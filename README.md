# Sentinel Zero - Proactive System Guard v1.4.3

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-blue.svg)](https://microsoft.com)
[![Build Status](https://img.shields.io/badge/Build-Passing-success.svg)]()

**Sentinel Zero** is an autonomous, real-time security suite designed to proactively block zero-day infostealers, credential harvest attacks, and malicious downloads across all file types.

Unlike traditional reactive antivirus scanners that analyze files *after* they are written to disk, **Sentinel Zero** places an **instant Windows API Exclusive Lock (`FILE_SHARE_NONE`)** on any file downloaded across all web browsers and directories *before* any application, background script, or user process can open or execute it.

---

## 📥 Downloads & Installation

### Option A: Automated PowerShell Web Installer (Recommended)
Open **PowerShell** and paste this 1-line command for instant background setup without Smart App Control blocks:
```powershell
irm https://raw.githubusercontent.com/TarangGarlapally/SentinelZero/master/install.ps1 | iex
```

### Option B: Windows Setup Wizard (.exe)
1. Download **`SentinelZero-Setup-v1.4.3.exe`** (33 MB) from the [Official Releases Page](https://github.com/TarangGarlapally/SentinelZero/releases/tag/v1.4.3).
2. If Windows 11 Smart App Control flags the downloaded installer:
   - **Method 1**: Run **`unblock_and_setup.bat`** (included in the release) to automatically unblock and launch the installer.
   - **Method 2**: Right-click `SentinelZero-Setup-v1.4.3.exe` $\rightarrow$ **Properties** $\rightarrow$ check **Unblock** at the bottom $\rightarrow$ click **Apply**.

### Option C: Run from Source / Python
```bash
# 1. Clone the repository
git clone https://github.com/TarangGarlapally/SentinelZero.git
cd SentinelZero

# 2. Run automated installer
powershell -ExecutionPolicy Bypass -File install.ps1
```

---

## Universal Protection Engine (System-Wide Folder Watcher & Multi-Select)

* 🌐 **Full System Folder Watchdog (`C:\Users\taran` / `%USERPROFILE%`)**: Monitors **EVERY SINGLE FOLDER AND SUBDIRECTORY** on your PC or multi-select specific folders (`Downloads`, `Desktop`, `Documents`, `Pictures`, `Videos`, custom paths). *Local code builds, text edits, and IDE file saves are ignored completely!*
* 📊 **Web Security Dashboard (`http://localhost:9090`)**: Local web interface displaying real-time protection statistics, live download inspection history (showing safe files & threats with exact scan findings), and interactive folder monitoring settings.
* 🔒 **Universal Real-Time File Locking**: Intercepts completed downloads across all browsers (Chrome, Edge, Brave, Firefox, Opera) and applies native Windows API locks (`0` share mode). No application can touch or execute the file while scanning is active (scan time: 50ms – 400ms).
* 🎯 **Infostealer Signature Engine**: Scans files against threat rules (`rules/infostealers.json`) targeting major stealer families (**Stealc, Lumma, RedLine, Raccoon, Vidar, Rhadamanthys, MetaStealer**).
* 📦 **Compressed Archive Recursive Inspector**: Unpacks `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, and `.iso` archives in memory to detect disguised executables, hidden payload scripts, double extensions (e.g. `invoice.pdf.exe`), and embedded runtimes.
* ⚡ **PE Executable & Binary Analyzer**: Evaluates Shannon entropy on `.exe`, `.msi`, `.dll`, and `.scr` files to catch packed/encrypted malware and audits API import tables for credential-harvesting functions (`CryptUnprotectData`, `sqlite3_open`).
* 📜 **Multi-Language Script Static Analyzer**: Heuristic AST parser for `.py`, `.ps1`, `.bat`, `.vbs`, and `.js` scripts targeting remote downloader calls (`urllib`, `requests`, `Invoke-WebRequest`, `WScript.Shell`), obfuscated Base64, and C2 IP literals.
* 🛡️ **Browser Cookie Vault Guard**: Continuously monitors Chrome, Edge, Brave, and Firefox `Cookies` database files and dynamically verifies Windows Authenticode digital signatures to protect session tokens against stealer malware.

---

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
