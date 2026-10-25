@echo off
rem Double-click to install WildWard Listen. Needs internet once; nothing is installed system-wide.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
if errorlevel 1 (echo. & echo Setup did not finish. See the message above.)
pause
