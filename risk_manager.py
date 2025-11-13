"""Risk management module."""

import config


class RiskManager:
    """Manage trading risk and position sizing."""
    
    def __init__(self, account_balance):
        self.account_balance = account_balance
        self.open_positions = []
        
    def calculate_position_size(self, stop_loss_pips, pip_value=10, confidence=0.5):
        """
        Calculate position size based on risk per trade and signal confidence.
        
        Args:
            stop_loss_pips: Stop loss in pips
            pip_value: Value per pip (depends on lot size and pair)
            confidence: Signal confidence (0-1), higher = larger position
        
        Returns:
            Position size in lots
        """
        # Base risk amount
        base_risk = self.account_balance * config.RISK_PER_TRADE
        
        # Adjust risk based on confidence
        # High confidence (>0.8): Use full risk
        # Medium confidence (0.5-0.8): Use 50-100% risk
        # Low confidence (<0.5): Use 25-50% risk
        if confidence > 0.8:
            risk_multiplier = 1.0
        elif confidence > 0.6:
            risk_multiplier = 0.75
        elif confidence > 0.4:
            risk_multiplier = 0.5
        else:
            risk_multiplier = 0.3  # Minimum position for weak signals
        
        risk_amount = base_risk * risk_multiplier
        position_size = risk_amount / (stop_loss_pips * pip_value)
        
        # Ensure minimum position size
        position_size = max(position_size, 0.01)
        
        return round(position_size, 2)
    
    def calculate_stop_loss(self, entry_price, signal, atr):
        """
        Calculate stop loss based on ATR.
        
        Args:
            entry_price: Entry price
            signal: 1 for buy, -1 for sell
            atr: Average True Range value
        
        Returns:
            Stop loss price
        """
        stop_distance = atr * 1.5  # 1.5x ATR
        
        if signal == 1:  # Buy
            stop_loss = entry_price - stop_distance
        else:  # Sell
            stop_loss = entry_price + stop_distance
            
        return stop_loss
    
    def calculate_take_profit(self, entry_price, stop_loss, signal):
        """
        Calculate take profit based on risk:reward ratio.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            signal: 1 for buy, -1 for sell
        
        Returns:
            Take profit price
        """
        risk = abs(entry_price - stop_loss)
        reward = risk * config.TAKE_PROFIT_RATIO
        
        if signal == 1:  # Buy
            take_profit = entry_price + reward
        else:  # Sell
            take_profit = entry_price - reward
            
        return take_profit
    
    def can_open_trade(self, max_positions=3):
        """Check if we can open a new trade."""
        return len(self.open_positions) < max_positions
    
    def add_position(self, position):
        """Add a new position."""
        self.open_positions.append(position)
    
    def close_position(self, position_id):
        """Close a position."""
        self.open_positions = [p for p in self.open_positions if p['id'] != position_id]
    
    def update_balance(self, profit_loss):
        """Update account balance after trade."""
        self.account_balance += profit_loss
        return self.account_balance
