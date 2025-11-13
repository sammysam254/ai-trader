"""Advanced ML model with deep learning for high-accuracy predictions."""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
import joblib
import config


class AdvancedTradingModel:
    """Advanced ensemble ML model for high-accuracy trading predictions."""
    
    def __init__(self):
        # Create ensemble of multiple models
        self.gb_model = GradientBoostingClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=7,
            min_samples_split=10,
            subsample=0.8,
            random_state=42
        )
        
        self.rf_model = RandomForestClassifier(
            n_estimators=300,
            max_depth=10,
            min_samples_split=8,
            random_state=42
        )
        
        self.nn_model = MLPClassifier(
            hidden_layer_sizes=(128, 64, 32),
            activation='relu',
            solver='adam',
            learning_rate='adaptive',
            max_iter=500,
            random_state=42
        )
        
        # Voting ensemble
        self.model = VotingClassifier(
            estimators=[
                ('gb', self.gb_model),
                ('rf', self.rf_model),
                ('nn', self.nn_model)
            ],
            voting='soft',
            weights=[2, 1, 1]  # GB gets more weight
        )
        
        self.scaler = StandardScaler()
        self.feature_columns = None
        
    def prepare_features(self, df):
        """Prepare features with advanced engineering."""
        # Drop non-feature columns
        exclude_cols = ['open', 'high', 'low', 'close', 'volume', 'target', 'signal']
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Add advanced features
        df_features = df[feature_cols].copy()
        
        # Price patterns
        df_features['price_range'] = df['high'] - df['low']
        df_features['body_size'] = abs(df['close'] - df['open'])
        df_features['upper_shadow'] = df['high'] - df[['close', 'open']].max(axis=1)
        df_features['lower_shadow'] = df[['close', 'open']].min(axis=1) - df['low']
        
        # Momentum features
        for period in [3, 5, 10, 20]:
            df_features[f'momentum_{period}'] = df['close'].pct_change(period)
            df_features[f'volatility_{period}'] = df['close'].rolling(period).std()
        
        # Trend strength
        df_features['trend_strength'] = abs(df_features.get('macd', 0)) * df_features.get('adx', 0) / 100
        
        # Remove NaN
        df_clean = df_features.dropna()
        
        self.feature_columns = df_clean.columns.tolist()
        return df_clean
    
    def create_target(self, df, forward_periods=2, profit_threshold=0.0002):
        """
        Create target for aggressive scalping (very small, quick profits).
        
        Args:
            df: DataFrame with price data
            forward_periods: Look ahead periods (2 for aggressive scalping)
            profit_threshold: 0.02% profit target for aggressive scalping
        """
        future_high = df['high'].shift(-forward_periods).rolling(forward_periods).max()
        future_low = df['low'].shift(-forward_periods).rolling(forward_periods).min()
        current_price = df['close']
        
        # Calculate potential profit for buy and sell
        buy_profit = (future_high - current_price) / current_price
        sell_profit = (current_price - future_low) / current_price
        
        # Determine best action
        target = np.where(
            (buy_profit > profit_threshold) & (buy_profit > sell_profit), 1,  # Buy
            np.where(
                (sell_profit > profit_threshold) & (sell_profit > buy_profit), -1,  # Sell
                0  # No trade
            )
        )
        
        return target
    
    def train(self, df):
        """Train the advanced ensemble model."""
        print("Training advanced AI model...")
        
        # Create target
        df['target'] = self.create_target(df)
        
        # Prepare features
        X = self.prepare_features(df)
        y = df.loc[X.index, 'target']
        
        # Remove neutral signals for training (focus on clear signals)
        mask = y != 0
        X = X[mask]
        y = y[mask]
        
        if len(X) < 100:
            print("Not enough data for training")
            return 0, 0
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train ensemble model
        print("Training ensemble (Gradient Boosting + Random Forest + Neural Network)...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        # Cross-validation score
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
        cv_mean = cv_scores.mean()
        
        print(f"Training accuracy: {train_score:.4f}")
        print(f"Testing accuracy: {test_score:.4f}")
        print(f"Cross-validation score: {cv_mean:.4f}")
        
        return train_score, test_score
    
    def predict(self, df):
        """Predict trade signals - ALWAYS return a signal for aggressive scalping."""
        X = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)
        
        # Get predictions and probabilities
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        # Get confidence (max probability)
        confidence = np.max(probabilities, axis=1)
        
        # For aggressive scalping, ALWAYS return the prediction
        # Even with low confidence, we trade (just with smaller position size)
        return predictions, confidence
    
    def save(self, filepath='advanced_model.pkl'):
        """Save model to disk."""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'features': self.feature_columns
        }, filepath)
        print(f"Advanced model saved to {filepath}")
    
    def load(self, filepath='advanced_model.pkl'):
        """Load model from disk."""
        data = joblib.load(filepath)
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_columns = data['features']
        print(f"Advanced model loaded from {filepath}")
