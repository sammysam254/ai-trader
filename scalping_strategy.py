"""Advanced scalping strategy with multiple confirmations."""

import numpy as np
import pandas as pd
from pattern_recognition import PatternRecognizer


class ScalpingStrategy:
    """High-frequency scalping strategy for quick profits."""
    
    def __init__(self):
        self.pattern_recognizer = PatternRecognizer()
        self.min_score = 3  # Lower threshold for aggressive scalping
        
    def analyze_scalping_opportunity(self, df):
        """Analyze for scalping opportunities with multiple confirmations."""
        if len(df) < 100:
            return pd.Series(0, index=df.index)
        
        # Initialize scores
        buy_score = pd.Series(0, index=df.index)
        sell_score = pd.Series(0, index=df.index)
        
        # 1. Trend Analysis (30% weight)
        trend_buy = (
            (df['close'] > df['ema_12']) &
            (df['ema_12'] > df['ema_26']) &
            (df['macd_diff'] > 0) &
            (df['adx'] > 20)  # Strong trend
        ).astype(int) * 3
        
        trend_sell = (
            (df['close'] < df['ema_12']) &
            (df['ema_12'] < df['ema_26']) &
            (df['macd_diff'] < 0) &
            (df['adx'] > 20)
        ).astype(int) * 3
        
        # 2. Momentum (25% weight)
        momentum_buy = (
            (df['rsi'] > 40) & (df['rsi'] < 60) &  # Not overbought
            (df['stoch_k'] > df['stoch_d']) &
            (df['roc'] > 0) &
            (df['tsi'] > 0)
        ).astype(int) * 2.5
        
        momentum_sell = (
            (df['rsi'] > 40) & (df['rsi'] < 60) &  # Not oversold
            (df['stoch_k'] < df['stoch_d']) &
            (df['roc'] < 0) &
            (df['tsi'] < 0)
        ).astype(int) * 2.5
        
        # 3. Volatility & Entry Timing (20% weight)
        # Look for volatility expansion (good for scalping)
        atr_expanding = df['atr'] > df['atr'].rolling(10).mean()
        bb_squeeze = (df['bb_high'] - df['bb_low']) < df['bb_width'].rolling(20).mean()
        
        volatility_buy = (
            atr_expanding &
            (df['close'] < df['bb_mid']) &  # Below middle band
            (df['close'] > df['bb_low'])    # Above lower band
        ).astype(int) * 2
        
        volatility_sell = (
            atr_expanding &
            (df['close'] > df['bb_mid']) &  # Above middle band
            (df['close'] < df['bb_high'])   # Below upper band
        ).astype(int) * 2
        
        # 4. Price Action Patterns (25% weight)
        patterns = self.pattern_recognizer.analyze_patterns(df)
        
        pattern_buy = (
            patterns['bullish_engulfing'] |
            patterns['hammer'] |
            patterns['morning_star'] |
            patterns['support_bounce']
        ).astype(int) * 2.5
        
        pattern_sell = (
            patterns['bearish_engulfing'] |
            patterns['shooting_star'] |
            patterns['evening_star'] |
            patterns['resistance_rejection']
        ).astype(int) * 2.5
        
        # 5. Volume Confirmation (if available)
        if 'volume' in df.columns and df['volume'].sum() > 0:
            volume_increasing = df['volume'] > df['volume'].rolling(10).mean()
            buy_score += volume_increasing.astype(int) * 0.5
            sell_score += volume_increasing.astype(int) * 0.5
        
        # Combine all scores
        buy_score = trend_buy + momentum_buy + volatility_buy + pattern_buy
        sell_score = trend_sell + momentum_sell + volatility_sell + pattern_sell
        
        # Generate signals - Only trade when there's a CLEAR opportunity
        # Require minimum score difference to avoid false signals
        min_score_diff = 2  # Require at least 2 point difference
        
        signals = np.where(
            (buy_score > sell_score) & (buy_score - sell_score >= min_score_diff), 1,  # Clear BUY
            np.where(
                (sell_score > buy_score) & (sell_score - buy_score >= min_score_diff), -1,  # Clear SELL
                0  # No clear signal - don't trade
            )
        )
        
        return pd.Series(signals, index=df.index), buy_score, sell_score
    
    def filter_scalping_signals(self, df, signals):
        """Apply filters to remove bad signals."""
        filtered = signals.copy()
        
        # Filter 1: Avoid extreme RSI (overbought/oversold)
        extreme_overbought = df['rsi'] > 75
        extreme_oversold = df['rsi'] < 25
        
        # Remove BUY signals when overbought, SELL signals when oversold
        filtered = np.where(extreme_overbought & (filtered == 1), 0, filtered)
        filtered = np.where(extreme_oversold & (filtered == -1), 0, filtered)
        
        # Filter 2: Require minimum ADX (trend strength)
        weak_trend = df['adx'] < 15
        filtered = np.where(weak_trend, 0, filtered)
        
        # Filter 3: Avoid trading during very low volatility
        low_volatility = df['atr'] < df['atr'].rolling(50).mean() * 0.5
        filtered = np.where(low_volatility, 0, filtered)
        
        return pd.Series(filtered, index=df.index)
    
    def calculate_scalping_targets(self, entry_price, signal, atr, buy_score, sell_score):
        """Calculate dynamic stop loss and take profit based on signal strength."""
        # Calculate signal strength
        total_score = abs(buy_score) + abs(sell_score)
        signal_strength = max(buy_score, sell_score) / max(total_score, 1)
        
        # Adjust targets based on signal strength
        # Stronger signals = wider targets, weaker signals = tighter targets
        if signal_strength > 7:  # Strong signal
            stop_multiplier = 1.2
            profit_multiplier = 2.0
        elif signal_strength > 5:  # Medium signal
            stop_multiplier = 1.0
            profit_multiplier = 1.5
        else:  # Weak signal - very tight scalping
            stop_multiplier = 0.8
            profit_multiplier = 1.2
        
        stop_distance = atr * stop_multiplier
        profit_distance = atr * profit_multiplier
        
        if signal == 1:  # Buy
            stop_loss = entry_price - stop_distance
            take_profit = entry_price + profit_distance
        else:  # Sell
            stop_loss = entry_price + stop_distance
            take_profit = entry_price - profit_distance
        
        return stop_loss, take_profit
