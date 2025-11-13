"""Machine learning model for trade prediction."""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import config


class TradingModel:
    """ML model for predicting trade signals."""
    
    def __init__(self):
        self.model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_columns = None
        
    def prepare_features(self, df):
        """Prepare features for ML model."""
        # Drop non-feature columns
        exclude_cols = ['open', 'high', 'low', 'close', 'volume', 'target', 'signal']
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Remove rows with NaN
        df_clean = df[feature_cols].dropna()
        
        self.feature_columns = feature_cols
        return df_clean
    
    def create_target(self, df, forward_periods=5, profit_threshold=0.001):
        """
        Create target variable based on future price movement.
        
        Args:
            df: DataFrame with price data
            forward_periods: How many periods ahead to look
            profit_threshold: Minimum profit to consider as winning trade
        
        Returns:
            1 for buy, -1 for sell, 0 for no trade
        """
        future_price = df['close'].shift(-forward_periods)
        current_price = df['close']
        
        price_change = (future_price - current_price) / current_price
        
        target = np.where(price_change > profit_threshold, 1,
                         np.where(price_change < -profit_threshold, -1, 0))
        
        return target
    
    def train(self, df):
        """Train the model on historical data."""
        # Create target
        df['target'] = self.create_target(df)
        
        # Prepare features
        X = self.prepare_features(df)
        y = df.loc[X.index, 'target']
        
        # Remove neutral signals for training
        mask = y != 0
        X = X[mask]
        y = y[mask]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=1-config.TRAIN_TEST_SPLIT, shuffle=False
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        print(f"Training accuracy: {train_score:.4f}")
        print(f"Testing accuracy: {test_score:.4f}")
        
        return train_score, test_score
    
    def predict(self, df):
        """Predict trade signals with confidence."""
        X = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)
        
        # Get predictions and probabilities
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        # Get confidence (max probability)
        confidence = np.max(probabilities, axis=1)
        
        # Filter by minimum confidence
        signals = np.where(confidence >= config.MIN_CONFIDENCE, predictions, 0)
        
        return signals, confidence
    
    def save(self, filepath='model.pkl'):
        """Save model to disk."""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'features': self.feature_columns
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load(self, filepath='model.pkl'):
        """Load model from disk."""
        data = joblib.load(filepath)
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_columns = data['features']
        print(f"Model loaded from {filepath}")
