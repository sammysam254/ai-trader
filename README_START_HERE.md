# 🚀 AI Forex Trader - START HERE

## ✅ What's Installed

- ✓ Python 3.11
- ✓ All Python packages
- ✓ Web application
- ✓ ML model
- ✓ 30+ indicators

## ⚠️ What's Missing

**MetaTrader 5 Terminal** - You need to install this to connect to real forex data.

---

## 🎯 Two Ways to Use This System

### Option 1: Demo Mode (Quick Start - No MT5 Needed)

**Best for:** Testing the system immediately

```cmd
START_DEMO_MODE.bat
```

Then open: **http://localhost:5000**

- Uses sample forex data
- All features work
- No MT5 installation required
- Perfect for learning the system

---

### Option 2: Real MT5 Connection (Recommended)

**Best for:** Real trading with live data

#### Step 1: Install MetaTrader 5

See detailed guide: **INSTALL_MT5.md**

Quick steps:
1. Download MT5 from a broker (IC Markets, XM, etc.)
2. Install it (takes 2 minutes)
3. Open a demo account (free, no risk)
4. Get your login credentials

#### Step 2: Start the Application

```cmd
START_TRADING.bat
```

Then open: **http://localhost:5000**

#### Step 3: Connect

1. Click "Connect MT5" button
2. Enter your credentials:
   - Login: Your account number
   - Password: Your MT5 password
   - Server: Your broker's server (e.g., "ICMarkets-Demo")
3. Click "Connect"

The system will automatically detect if it's a demo or real account!

---

## 📊 Using the Dashboard

### 1. Analyze Currency Pairs
- Select pair (EURUSD, GBPUSD, etc.)
- Select timeframe (H1, H4, D1)
- Click "Analyze"
- See BUY/SELL/NEUTRAL signal with confidence

### 2. Execute Trades
- After analysis, click "Execute Trade"
- Trade appears in "Open Positions"
- Monitor profit/loss in real-time

### 3. Run Backtests
- Click "Run Backtest"
- See win rate, total trades, returns
- Test different pairs and timeframes

### 4. Train ML Model
- Click "Train ML Model"
- Wait 1-2 minutes
- Model learns from historical data

### 5. Auto Trading
- Click "Start Auto Trading"
- System analyzes all pairs automatically
- Executes trades when signals appear
- Click "Stop Auto Trading" to pause

---

## 🔧 Troubleshooting

### "MT5 initialization failed"

**Solution:** Install MetaTrader 5
- See: **INSTALL_MT5.md**
- Or use demo mode: `START_DEMO_MODE.bat`

### "Failed to connect to MT5"

**Check:**
1. MT5 is installed
2. MT5 is closed (not running)
3. Login number is correct
4. Password is correct
5. Server name matches exactly

**Test connection:**
```cmd
.\venv311\Scripts\python.exe test_mt5_quick.py
```

### "Connection failed: Missing credentials"

**Solution:** Fill in all fields in the connection modal

### System Diagnostic

Run this to check everything:
```cmd
.\venv311\Scripts\python.exe diagnose.py
```

---

## 📱 Access from Phone/Tablet

1. Make sure phone is on same WiFi
2. Find your computer's IP: `ipconfig`
3. On phone browser: `http://YOUR_IP:5000`
4. Use the dashboard like on computer!

---

## 🎓 Learning Resources

### Files to Read:
- **INSTALL_MT5.md** - How to install MetaTrader 5
- **CONFIGURE_MT5.md** - How to find your credentials
- **SETUP_GUIDE.md** - Complete setup guide
- **QUICK_START.md** - Quick reference

### Test Scripts:
- **diagnose.py** - Check system status
- **test_mt5_quick.py** - Test MT5 connection
- **test_system.py** - Test all components

---

## ⚡ Quick Commands

```cmd
# Start with MT5 (real data)
START_TRADING.bat

# Start demo mode (sample data)
START_DEMO_MODE.bat

# Check system status
.\venv311\Scripts\python.exe diagnose.py

# Test MT5 connection
.\venv311\Scripts\python.exe test_mt5_quick.py

# Test system components
.\venv311\Scripts\python.exe test_system.py
```

---

## 🎯 Recommended Path

### For Beginners:
1. ✅ Start with **Demo Mode** (`START_DEMO_MODE.bat`)
2. ✅ Learn the interface
3. ✅ Test features
4. ✅ Then install MT5 for real data

### For Experienced Traders:
1. ✅ Install MT5 (see **INSTALL_MT5.md**)
2. ✅ Open demo account
3. ✅ Run `START_TRADING.bat`
4. ✅ Connect and start trading

---

## ⚠️ Important Warnings

- **Always test with demo account first**
- **Never risk more than you can afford to lose**
- **Past performance doesn't guarantee future results**
- **Use proper risk management (default: 2% per trade)**
- **This is for educational purposes**

---

## 🆘 Need Help?

1. **Check diagnostic:** `.\venv311\Scripts\python.exe diagnose.py`
2. **Read guides:** INSTALL_MT5.md, SETUP_GUIDE.md
3. **Test components:** Run test scripts
4. **Use demo mode:** If MT5 issues persist

---

## 🎉 Ready to Start!

Choose your path:

**Quick Test (No MT5):**
```cmd
START_DEMO_MODE.bat
```

**Real Trading (With MT5):**
```cmd
START_TRADING.bat
```

Open: **http://localhost:5000**

Happy Trading! 📈
