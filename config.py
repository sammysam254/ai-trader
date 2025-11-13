"""Configuration settings for the forex trading system."""

# Trading parameters
RISK_PER_TRADE = 0.02  # 2% risk per trade
STOP_LOSS_PIPS = 20
TAKE_PROFIT_RATIO = 2  # Risk:Reward ratio

# Indicator parameters
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20
BB_STD = 2
ATR_PERIOD = 14

# ML Model parameters
LOOKBACK_PERIOD = 100
TRAIN_TEST_SPLIT = 0.8
MIN_CONFIDENCE = 0.7  # Minimum prediction confidence for trade

# Currency pairs and commodities
CURRENCY_PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'XAUUSD']  # Added GOLD
