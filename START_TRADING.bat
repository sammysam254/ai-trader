@echo off
cls
echo.
echo ============================================================
echo           AI FOREX TRADER - QUICK START
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

REM Check MetaTrader5
echo Checking MetaTrader5 installation...
python -c "import metatrader5; print('MT5 Version:', metatrader5.__version__)" 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: MetaTrader5 not installed in this environment!
    echo.
    echo Installing MetaTrader5...
    python -m pip install MetaTrader5
    echo.
)

echo.
echo ============================================================
echo Starting AI Forex Trader...
echo ============================================================
echo.
echo Web Interface will open at: http://localhost:5000
echo.
echo Press CTRL+C to stop the server
echo.
echo ============================================================
echo.

REM Start the application
python app.py

pause
