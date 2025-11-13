# Install MetaTrader 5

## The Issue

You're getting this error:
```
MT5 initialization failed: (-10003, 'IPC initialize failed, MetaTrader 5 x64 not found')
```

This means **MetaTrader 5 terminal is not installed** on your computer.

## Solution: Install MetaTrader 5

### Step 1: Choose a Broker

You need to download MT5 from a forex broker. Popular options:

**For Demo Trading (Free, No Risk):**
- **IC Markets**: https://www.icmarkets.com/global/en/open-account/demo
- **XM**: https://www.xm.com/demo-account
- **Pepperstone**: https://pepperstone.com/en/demo-account
- **Admiral Markets**: https://admiralmarkets.com/start-trading/demo-account

### Step 2: Download & Install MT5

1. Go to your chosen broker's website
2. Click "Download MT5" or "Open Demo Account"
3. Download the MT5 installer
4. Run the installer (it will install to `C:\Program Files\MetaTrader 5\`)
5. Complete the installation

### Step 3: Open a Demo Account

1. Launch MetaTrader 5
2. It will prompt you to open an account
3. Choose **"Open a demo account"**
4. Fill in your details (use any name/email)
5. Choose account type: **Standard** or **Demo**
6. Set leverage: **1:100** or **1:500**
7. Set deposit: **$10,000** (virtual money)
8. Click **"Next"** and **"Finish"**

### Step 4: Get Your Credentials

After creating the demo account:

1. In MT5, go to **Tools → Options** (or press Ctrl+O)
2. Click the **"Server"** tab
3. Note down:
   - **Login**: Your account number (e.g., 12345678)
   - **Server**: Server name (e.g., "ICMarkets-Demo")
4. Your **Password**: The one you just created

### Step 5: Test Connection

Run this to verify MT5 is installed:

```cmd
.\venv311\Scripts\python.exe test_mt5_quick.py
```

If it says "✓ MT5 initialized successfully", you're good!

### Step 6: Start the Web App

```cmd
START_TRADING.bat
```

Then open: http://localhost:5000

Click "Connect MT5" and enter your credentials!

---

## Alternative: Use Demo Mode (No MT5 Required)

If you don't want to install MT5 right now, you can use the demo version:

```cmd
.\venv311\Scripts\python.exe app_demo.py
```

This uses sample data instead of real MT5 data, but all features work!

---

## Quick Links to Download MT5

### IC Markets (Recommended)
- Demo: https://www.icmarkets.com/global/en/open-account/demo
- Direct Download: https://download.mql5.com/cdn/web/ic.markets.sc/mt5/icmarkets5setup.exe

### XM
- Demo: https://www.xm.com/demo-account
- Download: https://download.mql5.com/cdn/web/xm.com/mt5/xmglobal5setup.exe

### Pepperstone
- Demo: https://pepperstone.com/en/demo-account
- Download: https://download.mql5.com/cdn/web/pepperstone.group.limited/mt5/pepperstone5setup.exe

---

## After Installing MT5

1. **Close MT5** (important for the connection to work)
2. Run: `START_TRADING.bat`
3. Open: http://localhost:5000
4. Click "Connect MT5"
5. Enter your demo account credentials
6. Start trading!

---

## Still Having Issues?

Run the diagnostic:
```cmd
.\venv311\Scripts\python.exe diagnose.py
```

If MT5 is installed correctly, it should show:
```
✓ MT5 initialized successfully
```
