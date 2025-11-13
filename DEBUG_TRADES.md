# Debug Trade Execution Issues

## Steps to Debug:

### 1. Restart Server with Full Logging
```powershell
.\RESTART_SERVER.bat
```

### 2. Watch Terminal Output
When you:
- Click "Execute Trade" - Watch for "TRADE EXECUTION" section
- Click "Close Position" - Watch for "CLOSE POSITION REQUEST" section

### 3. Common Issues and Solutions:

#### Trade Execution Fails:
**Check terminal for:**
- "Order failed: [error code]"
- "Symbol [SYMBOL] not found"
- "Invalid volume"

**Solutions:**
- Ensure market is open (Forex: Mon-Fri)
- Check symbol name is correct (EURUSD not EUR/USD)
- Verify sufficient margin
- Try s