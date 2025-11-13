@echo off
echo Stopping any running Python processes...
taskkill /F /IM python.exe 2>nul

echo.
echo Starting Advanced AI Forex Trader...
echo.

call venv311\Scripts\activate.bat
python app_advanced.py

pause
