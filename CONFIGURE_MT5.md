# Configure MT5 Connection

## Step 1: Find Your MT5 Credentials

### Open MetaTrader 5
1. Launch MetaTrader 5 on your computer
2. Go to **Tools → Options** (or press Ctrl+O)
3. Click on the **Server** tab

### Get Your Information:

**Login Number:**
- Displayed in the Server tab
- Example: 12345678

**Server Name:**
- Also in the Server tab
- Example: "ICMarkets-Demo" or "XM-Real"
- Copy the EXACT name shown

**Password:**
- The password you use to login to MT5
- If you forgot it, contact your broker

**MT5 Path:**
- Default: `C:\Program Files\MetaTrader 5\terminal64.exe`
- If you installed elsewhere, find your installation folder

## Step 2: Edit .env File

Open the `.env` file in this folder and replace:

```env
MT5_LOGIN=12345678
MT5_PASSWORD=YourPassword123
MT5_SERVER=ICMarkets-Demo
MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
```

## Step 3: Test Connection

Run this command to test:
```cmd
start_mt5_version.bat
```

Or manually:
```cmd
venv311\Scripts\activate.bat
python test_mt5_connection.py
```

## Common Issues

### "MT5 initialization failed"
- Check MT5_PATH is correct
- Make sure MT5 is installed
- Try running as Administrator

### "MT5 login failed"
- Verify login number (no spaces)
- Check password is correct
- Confirm server name matches exactly
- Make sure account is active

### "Symbol not found"
- Some brokers use different symbol names
- Try: EURUSD, EURUSDm, EURUSD.a
- Check your broker's symbol list in MT5

## Demo Account

If you don't have MT5 yet:

1. Download MT5 from your broker's website
2. Open a DEMO account (free, no risk)
3. Get your demo credentials
4. Use those in the .env file

Popular brokers with MT5:
- IC Markets
- XM
- Pepperstone
- FXCM
- Admiral Markets

## Ready to Start?

Once you've configured .env:

```cmd
start_mt5_version.bat
```

Then open: http://localhost:5000
