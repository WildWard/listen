@echo off
rem Starts WildWard Listen in its own window. Close that window to stop it. (Log: %USERPROFILE%\.wildward-listen.log)
if not exist "%~dp0.venv\Scripts\python.exe" (
  echo WildWard Listen is not installed yet. Double-click "Install WildWard Listen.bat" first.
  pause
  exit /b 1
)
cd /d "%~dp0"
start "" ".venv\Scripts\pythonw.exe" run.py --app %*
