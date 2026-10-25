# WildWard Listen installer for Windows. Run it by double-clicking "Install WildWard Listen.bat".
#
# Everything goes into this folder: a private Python (via uv), the app's packages, and nothing
# system-wide, so no admin rights are needed and deleting the folder removes it all.
# Needs internet once (about 1 GB in total, including the Perch 2.0 model). After that it works offline.

param([switch]$NoShortcut)   # -NoShortcut: skip the desktop shortcut (used for testing)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"   # Invoke-WebRequest is very slow with the progress bar on

$App = Split-Path -Parent $MyInvocation.MyCommand.Path
$Tools = Join-Path $App ".tools"
$UvVersion = "0.12.19"
$Uv = Join-Path $Tools "uv.exe"
$Venv = Join-Path $App ".venv"
$Py = Join-Path $Venv "Scripts\python.exe"

function Step($msg) { Write-Host ""; Write-Host "==> $msg" -ForegroundColor Green }

Write-Host "WildWard Listen setup" -ForegroundColor Yellow
Write-Host "Installing into $App"

New-Item -ItemType Directory -Force $Tools | Out-Null
$env:UV_PYTHON_INSTALL_DIR = Join-Path $Tools "python"
$env:UV_CACHE_DIR = Join-Path $Tools "cache"

if (-not (Test-Path $Uv)) {
    Step "Downloading the uv package manager $UvVersion"
    $zip = Join-Path $Tools "uv.zip"
    Invoke-WebRequest "https://github.com/astral-sh/uv/releases/download/$UvVersion/uv-x86_64-pc-windows-msvc.zip" -OutFile $zip
    Expand-Archive $zip -DestinationPath $Tools -Force
    Remove-Item $zip
}

if (-not (Test-Path $Py)) {
    Step "Setting up a private Python 3.12"
    & $Uv venv $Venv --python 3.12
    if ($LASTEXITCODE -ne 0) { throw "Could not create the Python environment." }
}

Step "Installing WildWard Listen's packages (the biggest step, a few minutes)"
& $Uv pip install --python $Py -r (Join-Path $App "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Package installation failed. Check the internet connection and run the installer again." }

Step "Downloading the Perch 2.0 sound model (about 400 MB, once) so Listen works offline in the field"
Push-Location $App
& $Py -c "from listen import embed; embed._load(); print('Perch 2.0 ready')"
$ok = $LASTEXITCODE
Pop-Location
if ($ok -ne 0) { Write-Host "The model download didn't finish. Listen will try again on its first scan (needs internet then)." -ForegroundColor Yellow }

if (-not $NoShortcut) {
    Step "Adding a 'WildWard Listen' shortcut to the desktop"
    $desktop = [Environment]::GetFolderPath("Desktop")
    $shell = New-Object -ComObject WScript.Shell
    $lnk = $shell.CreateShortcut((Join-Path $desktop "WildWard Listen.lnk"))
    $lnk.TargetPath = Join-Path $App "WildWard Listen.bat"
    $lnk.WorkingDirectory = $App
    $lnk.Description = "Offline bat-call review"
    $icon = Join-Path $App "listen\ui\icon.ico"
    if (Test-Path $icon) { $lnk.IconLocation = $icon }
    $lnk.Save()
}

Write-Host ""
Write-Host "Done. Double-click 'WildWard Listen' on your desktop to start." -ForegroundColor Green
