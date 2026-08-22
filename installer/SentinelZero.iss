; Inno Setup Script for Sentinel Zero - Proactive System Guard
#define MyAppName "Sentinel Zero"
#define MyAppVersion "1.4.2"
#define MyAppPublisher "Tarang Garlapally"
#define MyAppURL "https://github.com/TarangGarlapally/SentinelZero"
#define MyAppExeName "SentinelZero.exe"

[Setup]
AppId={{D89B5F9E-104A-4598-A8F2-3F9C985A901A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=C:\Users\taran\Projects\SentinelZero\LICENSE
OutputDir=C:\Users\taran\Projects\SentinelZero\dist
OutputBaseFilename=SentinelZero-Setup-v1.4.2
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=commandline
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName} Proactive System Guard

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Run Sentinel Zero automatically on Windows boot"; GroupDescription: "Windows Boot:"

[Files]
Source: "C:\Users\taran\Projects\SentinelZero\dist\SentinelZero\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\taran\Projects\SentinelZero\dist\SentinelZero\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: postinstall skipifsilent shellexec

[UninstallRun]
Filename: "taskkill.exe"; Parameters: "/F /IM SentinelZero.exe"; Flags: runhidden
Filename: "taskkill.exe"; Parameters: "/F /FI ""COMMANDLINE eq *app.py*"""; Flags: runhidden
Filename: "powershell.exe"; Parameters: "-Command ""Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*app.py*' -or $_.CommandLine -like '*SentinelZero*' } | Stop-Process -Force -ErrorAction SilentlyContinue"""; Flags: runhidden
