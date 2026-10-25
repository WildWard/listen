@echo off
rem Starts WildWard Listen and opens it in your browser. Close this window to stop it.
if not exist "%~dp0.venv\Scripts\python.exe" (
  echo WildWard Listen is not installed yet. Double-click "Install WildWard Listen.bat" first.
  pause
  exit /b 1
)
cd /d "%~dp0"
".venv\Scripts\python.exe" run.py %*
