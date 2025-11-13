"""Quick test of the AI trading system without MT5."""

print("Testing AI Forex Trading System...")
print("=" * 60)

# Test imports
print("\n[1/5] Testing imports...")
try:
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import GradientBoostingClassifier
    import ta
    print("✓ All core packages imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    exit(1)

# Test data generation
print("\n[2/5] Generating sample data...")
from data_loader import DataLoader
loader = DataLoader()
df = loader.generate_sample_data(periods=500, pair='EURUSD')
print(f"✓ Generated {len(df)} data points")

# Test indicators
print("\n[3/5] Calculating indicators...")
from indicators import IndicatorEngine
indicator_engine = IndicatorEngine(df)
df_indicators = indicator_engine.calculate_all()
print(f"✓ Calculated {len(df_indicators.columns) - 5} indicators")

# Test signal generation
print("\n[4/5] Generating signals...")
from signal_generator import SignalGenerator
signal_gen = SignalGenerator(df_indicators)
df_signals = signal_gen.generate_signals()
buy_signals = (df_signals['signal'] == 1).sum()
sell_signals = (df_signals['signal'] == -1).sum()
print(f"✓ Generated {buy_signals} BUY and {sell_signals} SELL signals")

# Test ML model
print("\n[5/5] Testing ML model...")
from ml_model import TradingModel
ml_model = TradingModel()
print("✓ ML model initialized")

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("=" * 60)
print("\nSystem is ready to use!")
print("\nNext steps:")
print("1. For web interface: python app.py")
print("2. For full backtest: python main.py")
print("3. For MT5 connection: Install Python 3.11 (see PYTHON_VERSION_FIX.md)")
