@echo off
cd /d "%~dp0"
echo === Luna Launcher: building EXE ===
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 py -m pip install -r requirements.txt pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed --name "LunaLauncher" --icon "assets\logo.ico" --add-data "assets;assets" --collect-all customtkinter --hidden-import pypresence luna_launcher.py
if errorlevel 1 py -m PyInstaller --noconfirm --clean --onefile --windowed --name "LunaLauncher" --icon "assets\logo.ico" --add-data "assets;assets" --collect-all customtkinter --hidden-import pypresence luna_launcher.py
echo.
echo Done: dist\LunaLauncher.exe
pause
