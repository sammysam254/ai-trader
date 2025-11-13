# GOLD (XAUUSD) TRADING ENABLED ✓

## What Was Added

GOLD (XAUUSD) has been added to the trading system and will now be:

1. **Available in the dropdown** - You can manually analyze and trade GOLD
2. **Included in auto-trading** - The AI will scan GOLD along with forex pairs
3. **Monitored every 60 seconds** - Same as other pairs

## Where GOLD Was Added

### 1. Auto-Trading Loop (`app_advanced.py`)
```python
# Now includes GOLD in the pairs list
pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'XAUUSD']
```

### 2. Config File (`config.py`)
```python
CURRENCY_PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'XAUUSD']
```

### 3. Web Interface (`templates/index_advanced.html`)
- Added "🥇 GOLD (XAU/USD)" to the symbol dropdown
- Positioned prominently in the list

## How to Trade GOLD

### Manual Trading:
1. Select "🥇 GOLD (XAU/USD)" from the dropdown
2. Click "Analyze"
3. System will analyze GOLD with all 30+ indicators
4. Execute trade if signal is good

### Auto-Trading:
1. Click "Start Auto Trading"
2. System will automatically scan GOLD every 60 seconds
3. Will execute GOLD trades when:
   - Clear signal (BUY or SELL)
   - Confidence 70%+
   - Both technical and ML agree

## GOLD Trading Characteristics

**Volatility:**
- GOLD is more volatile than forex pairs
- Larger pip movements
- ATR-based stops will be wider

**Spread:**
- GOLD typically has wider spreads than major forex pairs
- System accounts for this in entry price calculation

**Position Sizing:**
- Same $15 stake for auto-trading
- Position size automatically adjusted based on GOLD's volatility
- Smaller lot sizes due to higher pip value

**Best Timeframes for GOLD:**
- M5 (Scalping) - Fast moves
- M15 - Good balance
- H1 - Swing trading

## Expected Performance

GOLD tends to:
- ✅ Trend strongly (good for trend-following AI)
- ✅ Respect technical levels (patterns work well)
- ✅ Have clear momentum (RSI, MACD effective)
- ⚠️ Gap during news events (be cautious)
- ⚠️ Higher spread costs (factor in profitability)

## Testing GOLD

1. **Start the system:**
   ```cmd
   .\RUN_ADVANCED.bat
   ```

2. **Test manual analysis:**
   - Select GOLD from dropdown
   - Click "Analyze"
   - Check if signals make sense

3. **Test auto-trading:**
   - Start auto-trading
   - Watch logs for "Scanning XAUUSD..."
   - Should see GOLD analysis every 60 seconds

4. **Monitor results:**
   - GOLD trades will appear in positions list
   - Track P&L separately if desired

## Symbol Names by Broker

Different brokers may use different symbols for GOLD:
- **XAUUSD** - Most common (XAU = Gold, USD = US Dollar)
- **GOLD** - Some brokers
- **XAUUSD.** - With dot suffix
- **XAUUSD.m** - Mini lots

If your broker uses a different symbol, you can:
1. Check MT5 Market Watch for the exact symbol name
2. Update the dropdown in `templates/index_advanced.html`
3. Update the pairs list in `app_advanced.py`

## Notes

- GOLD is now fully integrated into the system
- Uses the same AI model and indicators as forex
- Same risk management rules apply
- Position sizes automatically adjusted for GOLD's characteristics
- Will be included in all future auto-trading scans

Happy GOLD trading! 🥇📈
