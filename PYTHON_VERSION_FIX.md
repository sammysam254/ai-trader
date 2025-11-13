# MetaTrader5 Python Version Issue

## Problem
The MetaTrader5 package is not compatible with Python 3.14. It only supports Python 3.8 through 3.11.

## Solution Options

### Option 1: Install Python 3.11 (Recommended)

1. **Download Python 3.11:**
   - Go to: https://www.python.org/downloads/
   - Download Python 3.11.x (latest 3.11 version)
   - During installation, check "Add Python to PATH"

2. **Create a virtual environment with Python 3.11:**
   ```powershell
   # Navigate to your project folder
   cd "C:\Users\Admin\Desktop\AI TRADER"
   
   # Create virtual environment with Python 3.11
   py -3.11 -m venv venv
   
   # Activate the virtual environment
   .\venv\Scripts\Activate.ps1
   
   # Install all packages
   python -m pip install -r requirements.txt
   ```

3. **Run the application:**
   ```powershell
   python app.py
   ```

### Option 2: Use Alternative Data Source (Temporary)

If you can't install Python 3.11 right now, I can modify the system to:
- Use demo/sample data for testing
- Connect to alternative APIs (Alpha Vantage, OANDA, etc.)
- Work without MT5 initially

### Option 3: Use Docker (Advanced)

Create a Docker container with Python 3.11:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## Quick Test Without MT5

You can still test the system with sample data:

```powershell
python main.py
```

This will:
- Generate sample forex data
- Calculate all indicators
- Train the ML model
- Run backtests
- Show you how the system works

## Checking Your Python Versions

```powershell
# List all installed Python versions
py --list

# Check specific version
py -3.11 --version
py -3.10 --version
```

## Recommended: Install Python 3.11

The easiest solution is to install Python 3.11 alongside your current Python 3.14:

1. Download from: https://www.python.org/ftp/python/3.11.11/python-3.11.11-amd64.exe
2. Run installer (keep "Add to PATH" checked)
3. Use `py -3.11` to run commands with Python 3.11

Then reinstall packages:
```powershell
py -3.11 -m pip install -r requirements.txt
py -3.11 app.py
```

## Need Help?

Let me know which option you prefer and I can help you set it up!
