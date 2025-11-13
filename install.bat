@echo off
echo Installing AI Forex Trader Dependencies...
echo.

echo [1/3] Installing core packages...
python -m pip install --upgrade pip
python -m pip install pandas numpy scikit-learn joblib

echo.
echo [2/3] Installing technical analysis and visualization...
python -m pip install ta matplotlib seaborn

echo.
echo [3/3] Installing web framework and MT5...
python -m pip install flask flask-cors python-dotenv MetaTrader5

echo.
echo Installation complete!
echo.
echo Next steps:
echo 1. Copy .env.example to .env
echo 2. Edit .env with your MT5 credentials
echo 3. Run: python app.py
echo.
pause
