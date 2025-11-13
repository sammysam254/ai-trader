@echo off
cls
echo.
echo ============================================================
echo      AI FOREX TRADER - DEMO MODE (No MT5 Required)
echo ============================================================
echo.
echo This mode uses sample data instead of real MT5 connection.
echo All features work, but data is simulated.
echo.
echo To use real MT5 data, install MetaTrader 5 first.
echo See: INSTALL_MT5.md
echo.
echo ============================================================
echo.

REM Check if venv exists
if not exist "venv311\Scripts\python.exe" (
    echo ERROR: Python 3.11 environment not found!
    echo.
    echo Please run: install_with_py311.bat first
    echo.
    pause
    exit /b 1
)

REM Activate environment
call venv311\Scripts\activate.bat

echo Starting Demo Mode...
echo.
echo Web Interface: http://localhost:5000
echo.
echo Press CTRL+C to stop
echo.
echo ============================================================
echo.

REM Start demo app
python app_demo.py

pause
