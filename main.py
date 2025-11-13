"""Main trading system execution."""

import pandas as pd
from data_loader import DataLoader
from indicators import IndicatorEngine
from signal_generator import SignalGenerator
from ml_model import TradingModel
from backtester import Backtester
import config


def main():
    """Run the complete trading system."""
    
    print("="*60)
    print("AI FOREX TRADING SYSTEM")
    print("="*60)
    
    # Step 1: Load data
    print("\n[1/6] Loading data...")
    loader = DataLoader()
    
    # Generate sample data (replace with real data loader)
    df = loader.generate_sample_data(periods=2000, pair='EURUSD')
    print(f"Loaded {len(df)} data points")
    
    # Step 2: Calculate indicators
    print("\n[2/6] Calculating 30+ technical indicators...")
    indicator_engine = IndicatorEngine(df)
    df_with_indicators = indicator_engine.calculate_all()
    print(f"Calculated {len(df_with_indicators.columns) - 5} indicators")
    
    # Step 3: Generate signals from indicators
    print("\n[3/6] Generating trading signals...")
    signal_gen = SignalGenerator(df_with_indicators)
    df_with_signals = signal_gen.generate_signals()
    
    # Step 4: Train ML model
    print("\n[4/6] Training machine learning model...")
    ml_model = TradingModel()
    train_score, test_score = ml_model.train(df_with_signals)
    
    # Step 5: Get ML predictions
    print("\n[5/6] Generating ML predictions...")
    ml_signals, ml_confidence = ml_model.predict(df_with_signals)
    
    # Combine indicator signals with ML
    df_final = signal_gen.combine_with_ml(df_with_signals, ml_signals, ml_confidence)
    df_final = signal_gen.filter_signals(df_final)
    
    # Count signals
    buy_signals = (df_final['final_signal'] == 1).sum()
    sell_signals = (df_final['final_signal'] == -1).sum()
    print(f"Generated {buy_signals} BUY and {sell_signals} SELL signals")
    
    # Step 6: Backtest strategy
    print("\n[6/6] Running backtest...")
    backtester = Backtester(initial_balance=10000)
    results = backtester.run(df_final)
    backtester.print_results(results)
    
    # Save model
    ml_model.save('forex_model.pkl')
    
    # Save results
    df_final.to_csv('trading_signals.csv')
    print("\nTrading signals saved to 'trading_signals.csv'")
    
    print("\n" + "="*60)
    print("SYSTEM READY FOR LIVE TRADING")
    print("="*60)
    print("\nIMPORTANT NOTES:")
    print("1. This system is for educational purposes")
    print("2. Always test with paper trading first")
    print("3. Past performance doesn't guarantee future results")
    print("4. Use proper risk management")
    print("5. Never risk more than you can afford to lose")
    
    return df_final, results


if __name__ == "__main__":
    df_final, results = main()
