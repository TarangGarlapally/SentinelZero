# Professional Windows Setup & Native App Installer for Sentinel Zero
$ErrorActionPreference = "Stop"

$appDir = "C:\Users\taran\Projects\SentinelZero"
$pythonwPath = "C:\Python314\pythonw.exe"
if (-not (Test-Path $pythonwPath)) {
    $pythonwPath = (Get-Command pythonw.exe).Source
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "       Sentinel Zero - Professional Windows Installer       " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Stop old running processes
Get-Process | Where-Object { $_.ProcessName -like "*SentinelZero*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# 2. Create Start Menu Shortcut (Sentinel Zero)
$startMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Sentinel Zero.lnk"
$wshell = New-Object -ComObject WScript.Shell
$shortcut = $wshell.CreateShortcut($startMenuPath)
$shortcut.TargetPath = $pythonwPath
$shortcut.Arguments = "`"$appDir\app.py`""
$shortcut.WorkingDirectory = $appDir
$shortcut.Description = "Sentinel Zero Proactive System Guard"
$shortcut.Save()

Write-Host "[*] Registered Start Menu Shortcut: Sentinel Zero" -ForegroundColor Green

# 3. Create Desktop Shortcut (Sentinel Zero)
$desktopPath = "$env:USERPROFILE\Desktop\Sentinel Zero.lnk"
$desktopShortcut = $wshell.CreateShortcut($desktopPath)
$desktopShortcut.TargetPath = $pythonwPath
$desktopShortcut.Arguments = "`"$appDir\app.py`""
$desktopShortcut.WorkingDirectory = $appDir
$desktopShortcut.Description = "Sentinel Zero Proactive System Guard"
$desktopShortcut.Save()

Write-Host "[*] Registered Desktop Shortcut: Sentinel Zero" -ForegroundColor Green

# 4. Register Windows Autostart Registry (HKCU:\Software\Microsoft\Windows\CurrentVersion\Run)
$registryPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$autostartCmd = "`"$pythonwPath`" `"$appDir\app.py`""
Set-ItemProperty -Path $registryPath -Name "SentinelZero" -Value $autostartCmd

Write-Host "[*] Registered Windows Boot Autostart (Silent Background Process)" -ForegroundColor Green

# 5. Launch Sentinel Zero silently right now
Write-Host "[*] Starting Sentinel Zero silent background guard..." -ForegroundColor Cyan
Start-Process -FilePath $pythonwPath -ArgumentList "`"$appDir\app.py`""

Write-Host "============================================================" -ForegroundColor Green
Write-Host " [SUCCESS] Sentinel Zero Installed & Active!" -ForegroundColor Green
Write-Host " - Search 'Sentinel Zero' in Windows Start Menu anytime" -ForegroundColor Green
Write-Host " - Runs completely silently in background with ZERO console windows" -ForegroundColor Green
Write-Host " - Web Security Dashboard Live at: http://localhost:9090" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
