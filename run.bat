@echo off
REM DICOM Importer PACS launcher
setlocal enabledelayedexpansion
cd /d "%~dp0"
.venv\Scripts\python.exe main.py
pause
