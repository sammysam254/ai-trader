@echo off
echo ============================================================
echo Installing AI Forex Trader with Python 3.11
echo ============================================================
echo.

call venv311\Scripts\activate.bat

echo [1/4] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [2/4] Installing core packages...
python -m pip install pandas numpy scikit-learn joblib

echo.
echo [3/4] Installing technical analysis...
python -m pip install ta matplotlib seaborn

echo.
echo [4/4] Installing Flask and MetaTrader5...
python -m pip install flask flask-cors python-dotenv MetaTrader5

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Copy .env.example to .env
echo 2. Edit .env with your MT5 credentials
echo 3. Run: start_mt5_version.bat
echo.
pause
