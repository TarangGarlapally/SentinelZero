@echo off
title Sentinel Zero Setup Launcher
echo ============================================================
echo      Sentinel Zero - Smart App Control Unblock & Setup
echo ============================================================
echo [*] Stripping Mark-of-the-Web (Zone.Identifier) tags...
powershell -Command "Get-ChildItem -Path '%~dp0' -Filter '*.exe' -ErrorAction SilentlyContinue | ForEach-Object { Unblock-File -Path $_.FullName }"
echo [*] Launching Sentinel Zero Setup Wizard...
if exist "%~dp0SentinelZero-Setup-v1.4.3.exe" (
    start "" "%~dp0SentinelZero-Setup-v1.4.3.exe"
) else if exist "%~dp0dist\SentinelZero-Setup-v1.4.3.exe" (
    start "" "%~dp0dist\SentinelZero-Setup-v1.4.3.exe"
) else (
    powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1"
)
