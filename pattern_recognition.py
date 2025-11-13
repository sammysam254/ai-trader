"""Advanced pattern recognition for chart analysis."""

import numpy as np
import pandas as pd


class PatternRecognizer:
    """Recognize chart patterns and price action."""
    
    def __init__(self):
        self.patterns_found = []
    
    def analyze_patterns(self, df):
        """Analyze and detect trading patterns."""
        patterns = {
            'bullish_engulfing': self.detect_bullish_engulfing(df),
            'bearish_engulfing': self.detect_bearish_engulfing(df),
            'hammer': self.detect_hammer(df),
            'shooting_star': self.detect_shooting_star(df),
            'morning_star': self.detect_morning_star(df),
            'evening_star': self.detect_evening_star(df),
            'double_bottom': self.detect_double_bottom(df),
            'double_top': self.detect_double_top(df),
            'support_bounce': self.detect_support_bounce(df),
            'resistance_rejection': self.detect_resistance_rejection(df)
        }
        
        return patterns
    
    def detect_bullish_engulfing(self, df):
        """Detect bullish engulfing pattern."""
        if len(df) < 2:
            return pd.Series(False, index=df.index)
        
        prev_bearish = df['close'].shift(1) < df['open'].shift(1)
        curr_bullish = df['close'] > df['open']
        engulfing = (df['open'] < df['close'].shift(1)) & (df['close'] > df['open'].shift(1))
        
        return prev_bearish & curr_bullish & engulfing
    
    def detect_bearish_engulfing(self, df):
        """Detect bearish engulfing pattern."""
        if len(df) < 2:
            return pd.Series(False, index=df.index)
        
        prev_bullish = df['close'].shift(1) > df['open'].shift(1)
        curr_bearish = df['close'] < df['open']
        engulfing = (df['open'] > df['close'].shift(1)) & (df['close'] < df['open'].shift(1))
        
        return prev_bullish & curr_bearish & engulfing
    
    def detect_hammer(self, df):
        """Detect hammer pattern (bullish reversal)."""
        body = abs(df['close'] - df['open'])
        lower_shadow = df[['close', 'open']].min(axis=1) - df['low']
        upper_shadow = df['high'] - df[['close', 'open']].max(axis=1)
        
        return (lower_shadow > body * 2) & (upper_shadow < body * 0.5)
    
    def detect_shooting_star(self, df):
        """Detect shooting star pattern (bearish reversal)."""
        body = abs(df['close'] - df['open'])
        upper_shadow = df['high'] - df[['close', 'open']].max(axis=1)
        lower_shadow = df[['close', 'open']].min(axis=1) - df['low']
        
        return (upper_shadow > body * 2) & (lower_shadow < body * 0.5)
    
    def detect_morning_star(self, df):
        """Detect morning star pattern (bullish reversal)."""
        if len(df) < 3:
            return pd.Series(False, index=df.index)
        
        first_bearish = df['close'].shift(2) < df['open'].shift(2)
        small_body = abs(df['close'].shift(1) - df['open'].shift(1)) < abs(df['close'].shift(2) - df['open'].shift(2)) * 0.3
        third_bullish = df['close'] > df['open']
        gap_down = df['open'].shift(1) < df['close'].shift(2)
        
        return first_bearish & small_body & third_bullish & gap_down
    
    def detect_evening_star(self, df):
        """Detect evening star pattern (bearish reversal)."""
        if len(df) < 3:
            return pd.Series(False, index=df.index)
        
        first_bullish = df['close'].shift(2) > df['open'].shift(2)
        small_body = abs(df['close'].shift(1) - df['open'].shift(1)) < abs(df['close'].shift(2) - df['open'].shift(2)) * 0.3
        third_bearish = df['close'] < df['open']
        gap_up = df['open'].shift(1) > df['close'].shift(2)
        
        return first_bullish & small_body & third_bearish & gap_up
    
    def detect_double_bottom(self, df, window=20):
        """Detect double bottom pattern (bullish)."""
        if len(df) < window * 2:
            return pd.Series(False, index=df.index)
        
        rolling_min = df['low'].rolling(window).min()
        is_local_min = df['low'] == rolling_min
        
        # Find two similar lows
        result = pd.Series(False, index=df.index)
        for i in range(window, len(df)):
            if is_local_min.iloc[i]:
                prev_mins = df['low'].iloc[i-window:i][is_local_min.iloc[i-window:i]]
                if len(prev_mins) > 0:
                    closest_min = prev_mins.iloc[-1]
                    if abs(df['low'].iloc[i] - closest_min) / closest_min < 0.002:  # Within 0.2%
                        result.iloc[i] = True
        
        return result
    
    def detect_double_top(self, df, window=20):
        """Detect double top pattern (bearish)."""
        if len(df) < window * 2:
            return pd.Series(False, index=df.index)
        
        rolling_max = df['high'].rolling(window).max()
        is_local_max = df['high'] == rolling_max
        
        # Find two similar highs
        result = pd.Series(False, index=df.index)
        for i in range(window, len(df)):
            if is_local_max.iloc[i]:
                prev_maxs = df['high'].iloc[i-window:i][is_local_max.iloc[i-window:i]]
                if len(prev_maxs) > 0:
                    closest_max = prev_maxs.iloc[-1]
                    if abs(df['high'].iloc[i] - closest_max) / closest_max < 0.002:  # Within 0.2%
                        result.iloc[i] = True
        
        return result
    
    def detect_support_bounce(self, df, window=50):
        """Detect price bouncing off support."""
        support = df['low'].rolling(window).min()
        near_support = (df['low'] - support) / support < 0.001  # Within 0.1% of support
        bouncing = df['close'] > df['open']  # Bullish candle
        
        return near_support & bouncing
    
    def detect_resistance_rejection(self, df, window=50):
        """Detect price rejecting resistance."""
        resistance = df['high'].rolling(window).max()
        near_resistance = (resistance - df['high']) / resistance < 0.001  # Within 0.1% of resistance
        rejecting = df['close'] < df['open']  # Bearish candle
        
        return near_resistance & rejecting
    
    def get_pattern_score(self, patterns):
        """Calculate overall pattern score."""
        bullish_patterns = ['bullish_engulfing', 'hammer', 'morning_star', 'double_bottom', 'support_bounce']
        bearish_patterns = ['bearish_engulfing', 'shooting_star', 'evening_star', 'double_top', 'resistance_rejection']
        
        bullish_score = sum([patterns[p].iloc[-1] if len(patterns[p]) > 0 else 0 for p in bullish_patterns])
        bearish_score = sum([patterns[p].iloc[-1] if len(patterns[p]) > 0 else 0 for p in bearish_patterns])
        
        return bullish_score, bearish_score
