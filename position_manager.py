"""Intelligent position manager that auto-closes trades when opportunity weakens."""

import time
from datetime import datetime
import threading


class PositionManager:
    """Manages open positions and auto-closes when signals reverse."""
    
    def __init__(self, mt5_connector, scalping_strategy, ml_model, data_loader):
        self.mt5 = mt5_connector
        self.scalping_strategy = scalping_strategy
        self.ml_model = ml_model
        self.data_loader = data_loader
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start monitoring open positions."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("Position monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring positions."""
        self.monitoring = False
        print("Position monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        from indicators import IndicatorEngine
        from trading_logger import trading_logger
        
        while self.monitoring:
            try:
                if not self.mt5.connected:
                    time.sleep(5)
                    continue
                
                # Get open positions
                positions = self.mt5.get_open_positions()
                
                if not positions:
                    time.sleep(5)
                    continue
                
                # Check each position
                for position in positions:
                    try:
                        symbol = position['symbol']
                        ticket = position['ticket']
                        position_type = position['type']  # 'buy' or 'sell'
                        entry_price = position['price_open']
                        current_price = position['price_current']
                        profit = position['profit']
                        
                        # Get current market data
                        df = self.mt5.get_historical_data(symbol, 'M5', bars=200)
                        if df is None:
                            continue
                        
                        # Calculate indicators
                        indicator_engine = IndicatorEngine(df)
                        df_indicators = indicator_engine.calculate_all()
                        
                        # Get current signals
                        signals, buy_score, sell_score = self.scalping_strategy.analyze_scalping_opportunity(df_indicators)
                        
                        # Get ML prediction
                        try:
                            ml_signals, ml_confidence = self.ml_model.predict(df_indicators)
                            current_ml_signal = ml_signals[-1] if len(ml_signals) > 0 else 0
                            current_confidence = ml_confidence[-1] if len(ml_confidence) > 0 else 0
                        except:
                            current_ml_signal = 0
                            current_confidence = 0
                        
                        current_signal = signals.iloc[-1]
                        latest_buy_score = buy_score.iloc[-1]
                        latest_sell_score = sell_score.iloc[-1]
                        
                        # NEW AUTO-CLOSE LOGIC: Only close if in profit OR loss > $10
                        should_close = False
                        close_reason = ""
                        
                        # Rule 1: ALWAYS close if in profit (any amount)
                        if profit > 0:
                            # Check if signal reversed or weakened
                            if position_type == 'buy' and current_signal == -1:
                                should_close = True
                                close_reason = f"Taking profit ${profit:.2f} - Signal reversed to SELL"
                            elif position_type == 'sell' and current_signal == 1:
                                should_close = True
                                close_reason = f"Taking profit ${profit:.2f} - Signal reversed to BUY"
                            # Also close if momentum is slowing and we have decent profit
                            elif profit > 2:
                                latest = df_indicators.iloc[-1]
                                momentum = abs(latest['close'] - df_indicators.iloc[-5]['close'])
                                if momentum < df_indicators['atr'].iloc[-1] * 0.3:
                                    should_close = True
                                    close_reason = f"Taking profit ${profit:.2f} - Momentum slowing"
                        
                        # Rule 2: ONLY close losing trades if loss > $10
                        elif profit < -10:
                            should_close = True
                            close_reason = f"Stop loss triggered - Loss ${profit:.2f} exceeds $10 limit"
                        
                        # Rule 3: Close if loss approaching $10 AND signal strongly reversed
                        elif profit < -7:
                            if position_type == 'buy' and current_signal == -1 and latest_sell_score > latest_buy_score + 3:
                                should_close = True
                                close_reason = f"Cutting loss ${profit:.2f} - Strong reversal detected"
                            elif position_type == 'sell' and current_signal == 1 and latest_buy_score > latest_sell_score + 3:
                                should_close = True
                                close_reason = f"Cutting loss ${profit:.2f} - Strong reversal detected"
                        
                        # Execute close if needed
                        if should_close:
                            trading_logger.warning(f"AUTO-CLOSING {symbol} {position_type.upper()} - {close_reason}")
                            trading_logger.info(f"  P&L: ${profit:.2f} | Buy Score: {latest_buy_score:.1f} | Sell Score: {latest_sell_score:.1f}")
                            
                            result = self.mt5.close_position(ticket)
                            if result:
                                trading_logger.success(f"Position {ticket} closed successfully")
                            else:
                                trading_logger.error(f"Failed to close position {ticket}")
                            
                            time.sleep(2)  # Brief pause after closing
                    
                    except Exception as e:
                        print(f"Error monitoring position {position.get('ticket', 'unknown')}: {str(e)}")
                        continue
                
                # Check every 10 seconds
                time.sleep(10)
                
            except Exception as e:
                print(f"Position monitoring error: {str(e)}")
                time.sleep(10)
