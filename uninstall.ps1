# 1-Click Complete Uninstaller & Deregistration Script for Sentinel Zero
$ErrorActionPreference = "SilentlyContinue"

Write-Host "============================================================" -ForegroundColor Red
Write-Host "      Sentinel Zero - Complete Uninstaller & Cleanup        " -ForegroundColor Red
Write-Host "============================================================" -ForegroundColor Red

# 1. Stop all Sentinel Zero processes & daemons
Write-Host "[*] Stopping all active Sentinel Zero processes..." -ForegroundColor Yellow
Get-Process | Where-Object { $_.ProcessName -like "*SentinelZero*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*app.py*" -or $_.CommandLine -like "*SentinelZero*" } | ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

# 2. Deregister Windows Autostart Registry Keys
Write-Host "[*] Deregistering Windows Autostart entries..." -ForegroundColor Yellow
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "SentinelZero" -ErrorAction SilentlyContinue
Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" -Name "SentinelZero" -ErrorAction SilentlyContinue

# 3. Deregister Windows Control Panel & Uninstall Registry Keys
Write-Host "[*] Cleaning up Windows Control Panel & Uninstall registry entries..." -ForegroundColor Yellow
$regPaths = @(
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{D89B5F9E-104A-4598-A8F2-3F9C985A901A}_is1",
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{D89B5F9E-104A-4598-A8F2-3F9C985A901A}_is1",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{D89B5F9E-104A-4598-A8F2-3F9C985A901A}_is1"
)
foreach ($rp in $regPaths) {
    if (Test-Path $rp) {
        Remove-Item -Path $rp -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# 4. Remove Start Menu and Desktop Shortcuts
Write-Host "[*] Removing Start Menu and Desktop shortcuts..." -ForegroundColor Yellow
$startMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Sentinel Zero.lnk"
$desktopPath = "$env:USERPROFILE\Desktop\Sentinel Zero.lnk"

if (Test-Path $startMenuPath) { Remove-Item -Path $startMenuPath -Force -ErrorAction SilentlyContinue }
if (Test-Path $desktopPath) { Remove-Item -Path $desktopPath -Force -ErrorAction SilentlyContinue }

# 5. Remove Application Data & Installation Directories
Write-Host "[*] Cleaning up application data & installation directories..." -ForegroundColor Yellow
$appDataDir = "$env:LOCALAPPDATA\SentinelZero"
$progDirs = @(
    "C:\Program Files\Sentinel Zero",
    "C:\Program Files (x86)\Sentinel Zero",
    "$env:LOCALAPPDATA\Programs\Sentinel Zero",
    "C:\Users\taran\Projects\SentinelZero\dist",
    "C:\Users\taran\Projects\SentinelZero\build"
)

if (Test-Path $appDataDir) { Remove-Item -Path $appDataDir -Recurse -Force -ErrorAction SilentlyContinue }
foreach ($p in $progDirs) {
    if (Test-Path $p) { Remove-Item -Path $p -Recurse -Force -ErrorAction SilentlyContinue }
}

Write-Host "============================================================" -ForegroundColor Green
Write-Host " [SUCCESS] Sentinel Zero completely uninstalled & deregistered!" -ForegroundColor Green
Write-Host " System is clean and ready for a fresh installation anytime." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
