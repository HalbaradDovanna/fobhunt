@echo off
REM Run this on your Windows machine (double-click it, or run from cmd)
REM It builds watcher.exe, select_region.exe, and capture_reference.exe
REM into the dist\ folder.

echo Installing dependencies...
python -m pip install -r requirements.txt pyinstaller

echo.
echo Building select_region.exe ...
python -m PyInstaller --onefile --noconsole --name select_region select_region.py

echo.
echo Building capture_reference.exe ...
python -m PyInstaller --onefile --name capture_reference capture_reference.py

echo.
echo Building watcher.exe ...
python -m PyInstaller --onefile --name watcher watcher.py

echo.
echo Done. Your .exe files are in the "dist" folder:
echo   dist\select_region.exe
echo   dist\capture_reference.exe
echo   dist\watcher.exe
echo.
echo Copy all three into one folder together. Run select_region.exe first,
echo then (for match mode) capture_reference.exe, then watcher.exe.
pause
