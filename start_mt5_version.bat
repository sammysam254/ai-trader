@echo off
echo ============================================================
echo Starting AI Forex Trader with MT5 Support
echo ============================================================
echo.

echo Activating Python 3.11 environment...
call venv311\Scripts\activate.bat

echo.
echo Python version:
python --version
echo.

echo Checking MetaTrader5 installation...
python -c "import MetaTrader5; print('MetaTrader5 version:', MetaTrader5.__version__)"
echo.

echo Starting web application...
python app.py

pause
