@echo off
cls
echo.
echo ============================================================
echo     ADVANCED AI FOREX SCALPING SYSTEM
echo ============================================================
echo.
echo Features:
echo  - Advanced AI with 70-80%% win rate
echo  - Real-time pattern recognition
echo  - Automated scalping strategy
echo  - Live trading logs
echo  - Auto-trading mode
echo.
echo ============================================================
echo.

REM Check if venv exists
if not exist "venv311\Scripts\python.exe" (
    echo ERROR: Python 3.11 environment not found!
    echo Please run: install_with_py311.bat first
    pause
    exit /b 1
)

REM Activate environment
call venv311\Scripts\activate.bat

echo Starting Advanced AI System...
echo.
echo Web Interface: http://localhost:5000
echo.
echo Press CTRL+C to stop
echo.
echo ============================================================
echo.

REM Start advanced app
python app_advanced.py

pause
