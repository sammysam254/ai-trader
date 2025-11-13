@echo off
echo ============================================================
echo Testing MT5 Connection
echo ============================================================
echo.

call venv311\Scripts\activate.bat
python test_mt5_connection.py

pause
