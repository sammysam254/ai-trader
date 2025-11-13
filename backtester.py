"""Backtesting engine for strategy evaluation."""

import pandas as pd
import numpy as np
from risk_manager import RiskManager
import config


class Backtester:
    """Backtest trading strategy on historical data."""
    
    def __init__(self, initial_balance=10000):
        self.initial_balance = initial_balance
        self.risk_manager = RiskManager(initial_balance)
        self.trades = []
        
    def run(self, df):
        """
        Run backtest on dataframe with signals.
        
        Args:
            df: DataFrame with 'final_signal' column
        
        Returns:
            Dictionary with backtest results
        """
        balance = self.initial_balance
        position = None
        
        for i in range(len(df)):
            row = df.iloc[i]
            
            # Check for exit signal
            if position is not None:
                # Check stop loss
                if position['type'] == 'buy':
                    if row['low'] <= position['stop_loss']:
                        pnl = position['stop_loss'] - position['entry']
                        balance += pnl * position['size']
                        self._record_trade(position, position['stop_loss'], pnl, 'stop_loss')
                        position = None
                        continue
                    # Check take profit
                    elif row['high'] >= position['take_profit']:
                        pnl = position['take_profit'] - position['entry']
                        balance += pnl * position['size']
                        self._record_trade(position, position['take_profit'], pnl, 'take_profit')
                        position = None
                        continue
                        
                else:  # sell position
                    if row['high'] >= position['stop_loss']:
                        pnl = position['entry'] - position['stop_loss']
                        balance += pnl * position['size']
                        self._record_trade(position, position['stop_loss'], pnl, 'stop_loss')
                        position = None
                        continue
                    elif row['low'] <= position['take_profit']:
                        pnl = position['entry'] - position['take_profit']
                        balance += pnl * position['size']
                        self._record_trade(position, position['take_profit'], pnl, 'take_profit')
                        position = None
                        continue
            
            # Check for entry signal
            if position is None and row['final_signal'] != 0:
                signal = row['final_signal']
                entry_price = row['close']
                atr = row['atr']
                
                # Calculate stop loss and take profit
                stop_loss = self.risk_manager.calculate_stop_loss(entry_price, signal, atr)
                take_profit = self.risk_manager.calculate_take_profit(entry_price, stop_loss, signal)
                
                # Calculate position size
                stop_pips = abs(entry_price - stop_loss) * 10000  # Convert to pips
                position_size = self.risk_manager.calculate_position_size(stop_pips)
                
                position = {
                    'entry': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'size': position_size,
                    'type': 'buy' if signal == 1 else 'sell',
                    'entry_time': df.index[i]
                }
        
        # Calculate statistics
        return self._calculate_statistics()
    
    def _record_trade(self, position, exit_price, pnl, exit_reason):
        """Record completed trade."""
        self.trades.append({
            'entry_price': position['entry'],
            'exit_price': exit_price,
            'type': position['type'],
            'pnl': pnl,
            'exit_reason': exit_reason,
            'entry_time': position['entry_time']
        })
    
    def _calculate_statistics(self):
        """Calculate backtest statistics."""
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'final_balance': self.initial_balance
            }
        
        df_trades = pd.DataFrame(self.trades)
        
        total_trades = len(df_trades)
        winning_trades = len(df_trades[df_trades['pnl'] > 0])
        losing_trades = len(df_trades[df_trades['pnl'] < 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = df_trades['pnl'].sum()
        avg_win = df_trades[df_trades['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = df_trades[df_trades['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        final_balance = self.initial_balance + total_pnl
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'final_balance': final_balance,
            'return_pct': ((final_balance - self.initial_balance) / self.initial_balance) * 100
        }
    
    def print_results(self, results):
        """Print backtest results."""
        print("\n" + "="*50)
        print("BACKTEST RESULTS")
        print("="*50)
        print(f"Total Trades: {results['total_trades']}")
        print(f"Winning Trades: {results['winning_trades']}")
        print(f"Losing Trades: {results['losing_trades']}")
        print(f"Win Rate: {results['win_rate']:.2f}%")
        print(f"Total P&L: ${results['total_pnl']:.2f}")
        print(f"Average Win: ${results['avg_win']:.2f}")
        print(f"Average Loss: ${results['avg_loss']:.2f}")
        print(f"Profit Factor: {results['profit_factor']:.2f}")
        print(f"Initial Balance: ${self.initial_balance:.2f}")
        print(f"Final Balance: ${results['final_balance']:.2f}")
        print(f"Return: {results['return_pct']:.2f}%")
        print("="*50)
