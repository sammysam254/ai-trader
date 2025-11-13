"""Trading signal generation combining indicators and ML."""

import numpy as np
import pandas as pd


class SignalGenerator:
    """Generate trading signals from indicators and ML predictions."""
    
    def __init__(self, df):
        self.df = df
        
    def generate_signals(self):
        """
        Generate trading signals based on multiple indicator confirmations.
        
        Returns:
            DataFrame with signal column (1=buy, -1=sell, 0=no trade)
        """
        df = self.df.copy()
        
        # Initialize signal scores
        buy_score = 0
        sell_score = 0
        
        # Trend signals
        trend_buy = (
            (df['close'] > df['sma_20']) & 
            (df['sma_20'] > df['sma_50']) &
            (df['macd_diff'] > 0) &
            (df['adx'] > 25)
        ).astype(int)
        
        trend_sell = (
            (df['close'] < df['sma_20']) & 
            (df['sma_20'] < df['sma_50']) &
            (df['macd_diff'] < 0) &
            (df['adx'] > 25)
        ).astype(int)
        
        # Momentum signals
        momentum_buy = (
            (df['rsi'] > 30) & (df['rsi'] < 70) &
            (df['stoch_k'] > df['stoch_d']) &
            (df['roc'] > 0)
        ).astype(int)
        
        momentum_sell = (
            (df['rsi'] > 30) & (df['rsi'] < 70) &
            (df['stoch_k'] < df['stoch_d']) &
            (df['roc'] < 0)
        ).astype(int)
        
        # Volatility signals
        volatility_buy = (
            (df['close'] < df['bb_low']) |
            (df['close'] < df['kc_low'])
        ).astype(int)
        
        volatility_sell = (
            (df['close'] > df['bb_high']) |
            (df['close'] > df['kc_high'])
        ).astype(int)
        
        # Price action signals
        price_action_buy = (
            (df['close'] > df['psar']) &
            (df['close'] > df['ichimoku_a'])
        ).astype(int)
        
        price_action_sell = (
            (df['close'] < df['psar']) &
            (df['close'] < df['ichimoku_a'])
        ).astype(int)
        
        # Combine signals
        df['buy_score'] = (trend_buy * 3 + momentum_buy * 2 + 
                          volatility_buy * 1 + price_action_buy * 2)
        df['sell_score'] = (trend_sell * 3 + momentum_sell * 2 + 
                           volatility_sell * 1 + price_action_sell * 2)
        
        # Generate final signal (require minimum score)
        min_score = 5
        df['signal'] = np.where(
            df['buy_score'] >= min_score, 1,
            np.where(df['sell_score'] >= min_score, -1, 0)
        )
        
        return df
    
    def combine_with_ml(self, df, ml_signals, ml_confidence):
        """
        Combine indicator signals with ML predictions.
        
        Args:
            df: DataFrame with indicator signals
            ml_signals: ML model predictions
            ml_confidence: ML prediction confidence
        
        Returns:
            Final combined signals
        """
        # Align indices
        df = df.copy()
        df['ml_signal'] = 0
        df['ml_confidence'] = 0
        
        df.loc[df.index[-len(ml_signals):], 'ml_signal'] = ml_signals
        df.loc[df.index[-len(ml_confidence):], 'ml_confidence'] = ml_confidence
        
        # Combine: both must agree for final signal
        df['final_signal'] = np.where(
            (df['signal'] == df['ml_signal']) & (df['ml_confidence'] > 0.7),
            df['signal'],
            0
        )
        
        return df
    
    def filter_signals(self, df):
        """Apply additional filters to reduce false signals."""
        df = df.copy()
        
        # Filter 1: Avoid ranging markets (low ADX)
        df.loc[df['adx'] < 20, 'final_signal'] = 0
        
        # Filter 2: Avoid extreme RSI
        df.loc[(df['rsi'] < 20) | (df['rsi'] > 80), 'final_signal'] = 0
        
        # Filter 3: Require minimum volatility
        df.loc[df['atr'] < df['atr'].rolling(20).mean() * 0.5, 'final_signal'] = 0
        
        # Filter 4: No conflicting signals in recent bars
        for i in range(1, 4):
            df.loc[df['final_signal'] != df['final_signal'].shift(i), 'final_signal'] = 0
        
        return df
