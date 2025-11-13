# Quick Start Guide

## Step 1: Install Dependencies

### Option A - Using PowerShell Script (Recommended)
```powershell
.\install.ps1
```

### Option B - Using Batch File
```cmd
install.bat
```

### Option C - Manual Installation
```powershell
python -m pip install --upgrade pip
python -m pip install pandas numpy scikit-learn joblib
python -m pip install ta matplotlib seaborn
python -m pip install flask flask-cors python-dotenv MetaTrader5
```

## Step 2: Configure MT5 Connection

1. Copy the example environment file:
```powershell
copy .env.example .env
```

2. Open `.env` in a text editor and fill in your MT5 details:
```env
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=your_broker_server
MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
```

### Finding Your MT5 Credentials:
- **Login**: Open MT5 → Tools → Options → Server tab
- **Server**: Same location, shows server name (e.g., "ICMarkets-Demo")
- **Password**: The password you use to login to MT5
- **Path**: Default is `C:\Program Files\MetaTrader 5\terminal64.exe`

## Step 3: Run the Application

```powershell
python app.py
```

The web interface will open at: **http://localhost:5000**

## Step 4: Use the Dashboard

1. Click **"Connect MT5"** button
2. Wait for connection (account info will load)
3. Select a currency pair (e.g., EURUSD)
4. Click **"Analyze"** to get trading signals
5. Click **"Execute Trade"** to place orders

## Troubleshooting

### "pip is not recognized"
Use `python -m pip` instead of just `pip`

### "MT5 initialization failed"
- Make sure MetaTrader 5 is installed
- Check the MT5_PATH in your .env file
- Try running PowerShell as Administrator

### "MT5 login failed"
- Verify your login, password, and server name
- Make sure your MT5 account is active
- Check your internet connection

### "Module not found" errors
Run the installation script again:
```powershell
.\install.ps1
```

## Access from Phone/Tablet

1. Find your computer's IP address:
```powershell
ipconfig
```

2. Look for "IPv4 Address" (e.g., 192.168.1.100)

3. On your phone/tablet browser, go to:
```
http://192.168.1.100:5000
```

Make sure both devices are on the same WiFi network!

## Important Warnings

⚠️ **ALWAYS TEST WITH DEMO ACCOUNT FIRST**
⚠️ **Never risk more than you can afford to lose**
⚠️ **Past performance doesn't guarantee future results**
⚠️ **Use proper risk management (default: 2% per trade)**

## Need Help?

Check the detailed `SETUP_GUIDE.md` for more information.
