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

# 1. Folder Monitoring Setup Choice
Write-Host "`n[?] Select Folder Monitoring Protection Mode:" -ForegroundColor Yellow
Write-Host "  [1] Monitor All System Folders (C:\Users\taran) [Recommended]" -ForegroundColor White
Write-Host "  [2] Choose Specific Folders (Multi-Select)" -ForegroundColor White

$choice = Read-Host "Enter Choice [1 or 2] (Default: 1)"

$configPath = "$appDir\config.json"
$config = @{}
if (Test-Path $configPath) {
    $config = Get-Content $configPath -Raw | ConvertFrom-Json
}

if ($choice -eq "2") {
    Write-Host "`n[?] Multi-Select Folders to Monitor (enter numbers separated by commas, e.g. 1,2 or 1,3):" -ForegroundColor Yellow
    Write-Host "  [1] Downloads Folder ($env:USERPROFILE\Downloads)" -ForegroundColor White
    Write-Host "  [2] Desktop Folder ($env:USERPROFILE\Desktop)" -ForegroundColor White
    Write-Host "  [3] Documents Folder ($env:USERPROFILE\Documents)" -ForegroundColor White
    Write-Host "  [4] Custom Directory Path" -ForegroundColor White

    $folderChoices = Read-Host "Enter folder numbers (Default: 1,2)"
    if (-not $folderChoices.Trim()) { $folderChoices = "1,2" }

    $selectedPaths = @()
    if ($folderChoices -like "*1*") { $selectedPaths += "$env:USERPROFILE\Downloads" }
    if ($folderChoices -like "*2*") { $selectedPaths += "$env:USERPROFILE\Desktop" }
    if ($folderChoices -like "*3*") { $selectedPaths += "$env:USERPROFILE\Documents" }
    if ($folderChoices -like "*4*") {
        $customPath = Read-Host "Enter custom directory path to monitor"
        if ($customPath -and (Test-Path $customPath)) { $selectedPaths += $customPath }
    }

    if ($selectedPaths.Count -eq 0) {
        $selectedPaths = @("$env:USERPROFILE\Downloads", "$env:USERPROFILE\Desktop")
    }

    Write-Host "`n[*] Selected ($($selectedPaths.Count)) Folders for Real-Time Monitoring:" -ForegroundColor Cyan
    foreach ($p in $selectedPaths) { Write-Host "   - $p" -ForegroundColor Green }

    $config | Add-Member -MemberType NoteProperty -Name "watch_mode" -Value "CUSTOM" -Force
    $config | Add-Member -MemberType NoteProperty -Name "watch_directories" -Value $selectedPaths -Force
    $config | Add-Member -MemberType NoteProperty -Name "custom_watch_directories" -Value $selectedPaths -Force
} else {
    Write-Host "`n[*] Monitoring All System Folders (C:\Users\taran)..." -ForegroundColor Cyan
    $config | Add-Member -MemberType NoteProperty -Name "watch_mode" -Value "ALL" -Force
    $config | Add-Member -MemberType NoteProperty -Name "watch_directories" -Value @("$env:USERPROFILE") -Force
}

$config | ConvertTo-Json -Depth 5 | Set-Content $configPath -Encoding UTF8
Write-Host "[*] Saved folder monitoring preferences to config.json" -ForegroundColor Green

# 2. Stop old running processes
Get-Process | Where-Object { $_.ProcessName -like "*SentinelZero*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# 3. Create Start Menu Shortcut (Sentinel Zero)
$startMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Sentinel Zero.lnk"
$wshell = New-Object -ComObject WScript.Shell
$shortcut = $wshell.CreateShortcut($startMenuPath)
$shortcut.TargetPath = $pythonwPath
$shortcut.Arguments = "`"$appDir\app.py`""
$shortcut.WorkingDirectory = $appDir
$shortcut.Description = "Sentinel Zero Proactive System Guard"
$shortcut.Save()

Write-Host "[*] Registered Start Menu Shortcut: Sentinel Zero" -ForegroundColor Green

# 4. Create Desktop Shortcut (Sentinel Zero)
$desktopPath = "$env:USERPROFILE\Desktop\Sentinel Zero.lnk"
$desktopShortcut = $wshell.CreateShortcut($desktopPath)
$desktopShortcut.TargetPath = $pythonwPath
$desktopShortcut.Arguments = "`"$appDir\app.py`""
$desktopShortcut.WorkingDirectory = $appDir
$desktopShortcut.Description = "Sentinel Zero Proactive System Guard"
$desktopShortcut.Save()

Write-Host "[*] Registered Desktop Shortcut: Sentinel Zero" -ForegroundColor Green

# 5. Register Windows Autostart Registry (HKCU:\Software\Microsoft\Windows\CurrentVersion\Run)
$registryPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$autostartCmd = "`"$pythonwPath`" `"$appDir\app.py`""
Set-ItemProperty -Path $registryPath -Name "SentinelZero" -Value $autostartCmd

Write-Host "[*] Registered Windows Boot Autostart (Silent Background Process)" -ForegroundColor Green

# 6. Launch Sentinel Zero silently right now
Write-Host "[*] Starting Sentinel Zero silent background guard..." -ForegroundColor Cyan
Start-Process -FilePath $pythonwPath -ArgumentList "`"$appDir\app.py`""

Write-Host "============================================================" -ForegroundColor Green
Write-Host " [SUCCESS] Sentinel Zero Installed & Active!" -ForegroundColor Green
Write-Host " - Search 'Sentinel Zero' in Windows Start Menu anytime" -ForegroundColor Green
Write-Host " - Change folder monitoring options anytime at: http://localhost:9090" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
