"""Data loading utilities for forex data."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class DataLoader:
    """Load and prepare forex data for analysis."""
    
    def load_csv(self, filepath):
        """
        Load forex data from CSV file.
        
        Expected columns: timestamp, open, high, low, close, volume
        """
        df = pd.read_csv(filepath)
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
        
        # Ensure required columns
        required = ['open', 'high', 'low', 'close']
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Add volume if missing
        if 'volume' not in df.columns:
            df['volume'] = 0
        
        return df
    
    def generate_sample_data(self, periods=1000, pair='EURUSD'):
        """
        Generate sample forex data for testing.
        
        Args:
            periods: Number of data points
            pair: Currency pair name
        
        Returns:
            DataFrame with OHLCV data
        """
        np.random.seed(42)
        
        # Starting price
        if pair == 'EURUSD':
            start_price = 1.1000
        elif pair == 'GBPUSD':
            start_price = 1.3000
        elif pair == 'USDJPY':
            start_price = 110.00
        else:
            start_price = 1.0000
        
        # Generate price movements
        returns = np.random.normal(0.0001, 0.01, periods)
        prices = start_price * (1 + returns).cumprod()
        
        # Generate OHLC
        data = []
        for i, close in enumerate(prices):
            high = close * (1 + abs(np.random.normal(0, 0.005)))
            low = close * (1 - abs(np.random.normal(0, 0.005)))
            open_price = prices[i-1] if i > 0 else start_price
            volume = np.random.randint(1000, 10000)
            
            data.append({
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        
        # Add timestamp index
        start_date = datetime.now() - timedelta(hours=periods)
        df.index = pd.date_range(start=start_date, periods=periods, freq='H')
        df.index.name = 'timestamp'
        
        return df
    
    def save_to_csv(self, df, filepath):
        """Save dataframe to CSV."""
        df.to_csv(filepath)
        print(f"Data saved to {filepath}")
