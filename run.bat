@echo off
cd /d "%~dp0"
python -m pip install -r requirements.txt >nul 2>&1
start "" pythonw luna_launcher.py
