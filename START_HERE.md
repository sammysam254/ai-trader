# 🚀 AI Forex Trader - Quick Start

## ✅ Your System is Ready!

The web application is now running at:

### 🖥️ On This Computer:
**http://localhost:5000**

### 📱 On Your Phone/Tablet (Same WiFi):
**http://10.2.70.240:5000**

---

## 🎯 What You Can Do Now

### 1. Open the Web Interface
- Click the link above or open your browser
- Go to: http://localhost:5000

### 2. Connect to Demo Mode
- Click the **"Connect MT5"** button
- It will connect to DEMO mode (using sample data)
- You'll see your demo account balance: $10,000

### 3. Analyze Currency Pairs
- Select a pair (EURUSD, GBPUSD, etc.)
- Select timeframe (H1, H4, D1)
- Click **"Analyze"**
- See BUY/SELL/NEUTRAL signal with confidence %

### 4. Execute Demo Trades
- After analysis, if signal is valid
- Click **"Execute Trade"**
- Watch it appear in "Open Positions"

### 5. Run Backtests
- Click **"Run Backtest"**
- See win rate, total trades, and returns
- Test different pairs and timeframes

### 6. Train ML Model
- Click **"Train ML Model"**
- Wait 1-2 minutes for training
- Model improves with more data

---

## 📊 Current Status

✅ **Python 3.14** - Installed  
✅ **All Packages** - Installed  
✅ **Web Server** - Running on port 5000  
✅ **ML Model** - Loaded and ready  
⚠️ **MT5 Connection** - Demo mode (sample data)  

---

## 🔄 To Use Real MT5 Data

The MetaTrader5 package requires Python 3.8-3.11 (not 3.14).

### Quick Fix:
1. Install Python 3.11 from: https://www.python.org/downloads/
2. Create virtual environment:
   ```powershell
   py -3.11 -m venv venv
   .\venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```
3. Run with MT5:
   ```powershell
   python app.py
   ```

See **PYTHON_VERSION_FIX.md** for detailed instructions.

---

## 🎮 How to Use the Dashboard

### Left Panel - Account Info
- Balance, Equity, Profit
- Trading controls
- Model training

### Center Panel - Analysis
- Select pair and timeframe
- Get AI trading signals
- View technical indicators
- Execute trades

### Right Panel - Positions
- View open trades
- Monitor profit/loss
- Close positions

---

## 🛑 To Stop the Server

Press **CTRL+C** in the terminal

Or run:
```powershell
# Find the process
Get-Process python | Where-Object {$_.MainWindowTitle -like "*app_demo*"}

# Stop it
Stop-Process -Name python
```

---

## 📱 Access from Phone

1. Make sure phone is on same WiFi as computer
2. Open browser on phone
3. Go to: **http://10.2.70.240:5000**
4. Use the dashboard just like on computer!

---

## ⚠️ Important Notes

### Demo Mode Features:
- ✅ All indicators working (30+)
- ✅ ML model predictions
- ✅ Signal generation
- ✅ Backtesting
- ✅ Demo trading
- ⚠️ Uses sample data (not real market)

### For Real Trading:
1. Install Python 3.11
2. Install MetaTrader5 package
3. Configure .env with MT5 credentials
4. Use app.py instead of app_demo.py

---

## 🎯 Next Steps

1. **Test the System**
   - Analyze different pairs
   - Run backtests
   - Execute demo trades

2. **Train the Model**
   - Click "Train ML Model"
   - Let it learn from data
   - Improves accuracy

3. **Understand the Signals**
   - BUY = Bullish signal
   - SELL = Bearish signal
   - NEUTRAL = No clear direction
   - Confidence = ML certainty (70%+ recommended)

4. **Setup Real MT5** (Optional)
   - Follow PYTHON_VERSION_FIX.md
   - Install Python 3.11
   - Connect to real broker

---

## 🆘 Need Help?

- **System not working?** Check test_system.py
- **Can't access web?** Check firewall settings
- **Want real MT5?** Read PYTHON_VERSION_FIX.md
- **Full guide?** See SETUP_GUIDE.md

---

## 🎉 You're All Set!

Open your browser and start trading:
**http://localhost:5000**

Happy Trading! 📈
