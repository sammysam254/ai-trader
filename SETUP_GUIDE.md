# AI Forex Trader - Setup Guide

## Prerequisites

1. **Python 3.8+** installed
2. **MetaTrader 5** installed (download from your broker)
3. **MT5 Demo or Live Account** credentials

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Edit `.env` file with your credentials:

```env
# MetaTrader 5 Configuration
MT5_LOGIN=12345678
MT5_PASSWORD=YourPassword123
MT5_SERVER=YourBroker-Demo
MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe

# Trading Configuration
INITIAL_BALANCE=10000
MAX_POSITIONS=3
RISK_PER_TRADE=0.02
MIN_CONFIDENCE=0.70

# Flask Configuration
FLASK_SECRET_KEY=change-this-to-random-string
FLASK_ENV=production
FLASK_DEBUG=False
HOST=0.0.0.0
PORT=5000
```

### 3. Find Your MT5 Credentials

**Login & Password:**
- Open MetaTrader 5
- Go to Tools → Options → Server
- Your login number is displayed there

**Server Name:**
- Same location as above
- Example: "ICMarkets-Demo", "XM-Real", etc.

**MT5 Path:**
- Windows default: `C:\Program Files\MetaTrader 5\terminal64.exe`
- If installed elsewhere, find your installation path

### 4. Train the ML Model (First Time)

```bash
python main.py
```

This will:
- Generate sample data (or use your MT5 data)
- Calculate 30+ indicators
- Train the ML model
- Run a backtest
- Save the model as `forex_model.pkl`

### 5. Start the Web Application

```bash
python app.py
```

The web interface will be available at:
- Local: http://localhost:5000
- Network: http://YOUR_IP:5000

## Using the Web Interface

### 1. Connect to MT5
- Click "Connect MT5" button
- Wait for connection confirmation
- Account info will load automatically

### 2. Analyze a Pair
- Select currency pair (e.g., EURUSD)
- Select timeframe (e.g., H1)
- Click "Analyze"
- View signal (BUY/SELL/NEUTRAL) and confidence

### 3. Execute Manual Trade
- After analysis, if signal is valid
- Click "Execute Trade"
- Confirm the trade
- Position will appear in "Open Positions"

### 4. Run Backtest
- Select pair and timeframe
- Click "Run Backtest"
- View win rate, total trades, and return

### 5. Train Model
- Click "Train ML Model"
- Wait for training to complete
- Model will be saved automatically

### 6. Start Automated Trading
- Click "Start Auto Trading"
- System will analyze all configured pairs
- Trades execute automatically when signals appear
- Click "Stop Auto Trading" to pause

## Important Notes

### Risk Management
- Default risk: 2% per trade
- Maximum 3 positions open
- Stop loss: 1.5x ATR
- Take profit: 2:1 risk/reward

### Testing First
1. **Use Demo Account** - Never start with real money
2. **Paper Trade** - Test for at least 1-2 months
3. **Monitor Results** - Track win rate and drawdown
4. **Adjust Parameters** - Tune based on results

### Common Issues

**"MT5 initialization failed"**
- Check MT5_PATH is correct
- Make sure MT5 is installed
- Try running as administrator

**"MT5 login failed"**
- Verify login, password, and server name
- Check internet connection
- Ensure account is active

**"Failed to get data"**
- Symbol might not be available
- Check symbol name format (EURUSD not EUR/USD)
- Verify market is open

**"No module named 'MetaTrader5'"**
- Run: `pip install MetaTrader5`
- MT5 package only works on Windows

## Accessing from Other Devices

### Same Network
1. Find your computer's IP address:
   ```bash
   ipconfig
   ```
2. Look for "IPv4 Address" (e.g., 192.168.1.100)
3. Access from phone/tablet: http://192.168.1.100:5000

### Internet Access (Advanced)
1. Set up port forwarding on router (port 5000)
2. Use dynamic DNS service
3. Or deploy to cloud (AWS, DigitalOcean, etc.)

## Cloud Deployment (Optional)

### Deploy to Heroku
```bash
# Install Heroku CLI
heroku login
heroku create your-forex-trader
git push heroku main
```

### Deploy to AWS EC2
1. Launch Ubuntu instance
2. Install Python and dependencies
3. Configure security group (port 5000)
4. Run with gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

## Security Recommendations

1. **Change Secret Key** - Use random string in .env
2. **Use HTTPS** - Set up SSL certificate for production
3. **Add Authentication** - Implement login system
4. **Firewall Rules** - Restrict access to known IPs
5. **Never Commit .env** - Keep credentials private

## Support

For issues or questions:
1. Check MT5 terminal for errors
2. Review Flask console logs
3. Test with demo account first
4. Verify all credentials are correct

## Disclaimer

This system is for educational purposes. Forex trading carries significant risk. Always:
- Test thoroughly before live trading
- Never risk more than you can afford to lose
- Use proper risk management
- Past performance doesn't guarantee future results
