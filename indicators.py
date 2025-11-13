"""Technical indicators calculation module."""

import pandas as pd
import numpy as np
from ta.trend import (SMAIndicator, EMAIndicator, MACD, ADXIndicator, 
                      CCIIndicator, IchimokuIndicator, PSARIndicator)
from ta.momentum import (RSIIndicator, StochasticOscillator, 
                         WilliamsRIndicator, ROCIndicator, TSIIndicator)
from ta.volatility import (BollingerBands, AverageTrueRange, 
                           KeltnerChannel, DonchianChannel)
from ta.volume import (OnBalanceVolumeIndicator, ChaikinMoneyFlowIndicator,
                       ForceIndexIndicator, MFIIndicator)


class IndicatorEngine:
    """Calculate 30+ technical indicators for forex trading."""
    
    def __init__(self, df):
        """
        Initialize with OHLCV dataframe.
        
        Args:
            df: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
        """
        self.df = df.copy()
        
    def calculate_all(self):
        """Calculate all indicators and return enhanced dataframe."""
        df = self.df
        
        # Trend Indicators
        df['sma_20'] = SMAIndicator(df['close'], window=20).sma_indicator()
        df['sma_50'] = SMAIndicator(df['close'], window=50).sma_indicator()
        df['sma_200'] = SMAIndicator(df['close'], window=200).sma_indicator()
        df['ema_12'] = EMAIndicator(df['close'], window=12).ema_indicator()
        df['ema_26'] = EMAIndicator(df['close'], window=26).ema_indicator()
        
        macd = MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        adx = ADXIndicator(df['high'], df['low'], df['close'])
        df['adx'] = adx.adx()
        df['adx_pos'] = adx.adx_pos()
        df['adx_neg'] = adx.adx_neg()
        
        df['cci'] = CCIIndicator(df['high'], df['low'], df['close']).cci()
        
        ichimoku = IchimokuIndicator(df['high'], df['low'])
        df['ichimoku_a'] = ichimoku.ichimoku_a()
        df['ichimoku_b'] = ichimoku.ichimoku_b()
        
        df['psar'] = PSARIndicator(df['high'], df['low'], df['close']).psar()
        
        # Momentum Indicators
        df['rsi'] = RSIIndicator(df['close'], window=14).rsi()
        
        stoch = StochasticOscillator(df['high'], df['low'], df['close'])
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        
        df['williams_r'] = WilliamsRIndicator(df['high'], df['low'], df['close']).williams_r()
        df['roc'] = ROCIndicator(df['close']).roc()
        df['tsi'] = TSIIndicator(df['close']).tsi()
        
        # Volatility Indicators
        bb = BollingerBands(df['close'])
        df['bb_high'] = bb.bollinger_hband()
        df['bb_mid'] = bb.bollinger_mavg()
        df['bb_low'] = bb.bollinger_lband()
        df['bb_width'] = bb.bollinger_wband()
        
        df['atr'] = AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()
        
        kc = KeltnerChannel(df['high'], df['low'], df['close'])
        df['kc_high'] = kc.keltner_channel_hband()
        df['kc_low'] = kc.keltner_channel_lband()
        
        dc = DonchianChannel(df['high'], df['low'], df['close'])
        df['dc_high'] = dc.donchian_channel_hband()
        df['dc_low'] = dc.donchian_channel_lband()
        
        # Volume Indicators (if volume available)
        if 'volume' in df.columns and df['volume'].sum() > 0:
            df['obv'] = OnBalanceVolumeIndicator(df['close'], df['volume']).on_balance_volume()
            df['cmf'] = ChaikinMoneyFlowIndicator(df['high'], df['low'], df['close'], df['volume']).chaikin_money_flow()
            df['fi'] = ForceIndexIndicator(df['close'], df['volume']).force_index()
            df['mfi'] = MFIIndicator(df['high'], df['low'], df['close'], df['volume']).money_flow_index()
        
        # Custom indicators
        df['price_momentum'] = df['close'].pct_change(periods=10)
        df['volatility'] = df['close'].rolling(window=20).std()
        
        return df
