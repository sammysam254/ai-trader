"""MetaTrader 5 connector for live data and trading."""

try:
    import metatrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("WARNING: MetaTrader5 package not available. Install with: pip install MetaTrader5")
    print("Note: MetaTrader5 requires Python 3.8-3.11. You may need to use an older Python version.")

import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class MT5Connector:
    """Connect to MetaTrader 5 for data and trading."""
    
    def __init__(self):
        self.connected = False
        self.login = os.getenv('MT5_LOGIN')
        self.password = os.getenv('MT5_PASSWORD')
        self.server = os.getenv('MT5_SERVER')
        self.path = os.getenv('MT5_PATH')
        
        if not MT5_AVAILABLE:
            print("MT5 module not available. Some features will be disabled.")
        
    def connect(self):
        """Initialize connection to MT5."""
        if not MT5_AVAILABLE:
            print("ERROR: MetaTrader5 package not installed")
            return False
        
        try:
            import metatrader5 as mt5_lib
            
            print("Initializing MT5...")
            
            # IMPORTANT: Try without path first (more reliable)
            print("Trying default MT5 initialization...")
            init_result = mt5_lib.initialize()
            
            if not init_result:
                error = mt5_lib.last_error()
                print(f"Default init failed: {error}")
                
                # Only try with path if default failed
                if self.path and self.path.strip():
                    print(f"Trying with custom path: {self.path}")
                    init_result = mt5_lib.initialize(path=self.path)
                    
                    if not init_result:
                        error = mt5_lib.last_error()
                        print(f"Init with path also failed: {error}")
                        print("\nPossible issues:")
                        print("1. MT5 is not installed")
                        print("2. MT5 is currently running (close it first)")
                        print("3. Path is incorrect")
                        return False
            
            print("✓ MT5 initialized successfully")
            
            # Login to account if credentials provided
            if self.login and self.password and self.server:
                print(f"Logging in to {self.server}...")
                
                try:
                    login_num = int(self.login)
                except ValueError:
                    print(f"✗ Invalid login number: {self.login}")
                    mt5_lib.shutdown()
                    return False
                
                print(f"Attempting login with account {login_num}...")
                authorized = mt5_lib.login(
                    login=login_num,
                    password=self.password,
                    server=self.server
                )
                
                if not authorized:
                    error = mt5_lib.last_error()
                    print(f"✗ MT5 login failed: {error}")
                    print(f"   Login: {login_num}")
                    print(f"   Server: {self.server}")
                    print("\nCheck:")
                    print("1. Login number is correct")
                    print("2. Password is correct")
                    print("3. Server name matches exactly (case-sensitive)")
                    print("4. Account is active")
                    mt5_lib.shutdown()
                    return False
                
                print("✓ Login successful")
            
            self.connected = True
            print("✓ Connected to MT5 successfully")
            return True
            
        except Exception as e:
            print(f"✗ MT5 connection exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def disconnect(self):
        """Close MT5 connection."""
        mt5.shutdown()
        self.connected = False
        print("Disconnected from MT5")
    
    def get_historical_data(self, symbol, timeframe='H1', bars=1000):
        """
        Get historical price data.
        
        Args:
            symbol: Currency pair (e.g., 'EURUSD')
            timeframe: Timeframe (M1, M5, M15, M30, H1, H4, D1)
            bars: Number of bars to retrieve
        
        Returns:
            DataFrame with OHLCV data
        """
        if not self.connected:
            self.connect()
        
        # Map timeframe string to MT5 constant
        timeframe_map = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1
        }
        
        tf = timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)
        
        # Get rates
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)
        
        if rates is None:
            print(f"Failed to get data: {mt5.last_error()}")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        # Rename columns
        df.rename(columns={
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'tick_volume': 'volume'
        }, inplace=True)
        
        return df[['open', 'high', 'low', 'close', 'volume']]
    
    def get_current_price(self, symbol):
        """Get current bid/ask price."""
        if not self.connected:
            self.connect()
        
        tick = mt5.symbol_info_tick(symbol)
        
        if tick is None:
            return None
        
        return {
            'bid': tick.bid,
            'ask': tick.ask,
            'time': datetime.fromtimestamp(tick.time)
        }
    
    def place_order(self, symbol, order_type, volume, price=None, sl=None, tp=None, comment="AI Trader"):
        """
        Place a trading order.
        
        Args:
            symbol: Currency pair
            order_type: 'buy' or 'sell'
            volume: Lot size
            price: Entry price (None for market order)
            sl: Stop loss price
            tp: Take profit price
            comment: Order comment
        
        Returns:
            Order result
        """
        if not MT5_AVAILABLE:
            print("MT5 not available")
            return None
            
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            import metatrader5 as mt5_lib
            
            # Get symbol info
            symbol_info = mt5_lib.symbol_info(symbol)
            if symbol_info is None:
                print(f"Symbol {symbol} not found")
                return None
            
            # Enable symbol if not enabled
            if not symbol_info.visible:
                if not mt5_lib.symbol_select(symbol, True):
                    print(f"Failed to select {symbol}")
                    return None
            
            # Get current price
            tick = mt5_lib.symbol_info_tick(symbol)
            if tick is None:
                print(f"Failed to get tick for {symbol}")
                return None
            
            # Prepare request
            if order_type.lower() == 'buy':
                trade_type = mt5_lib.ORDER_TYPE_BUY
                price = tick.ask if price is None else price
            else:
                trade_type = mt5_lib.ORDER_TYPE_SELL
                price = tick.bid if price is None else price
            
            # Round volume to symbol's volume step
            volume = round(volume / symbol_info.volume_step) * symbol_info.volume_step
            volume = max(symbol_info.volume_min, min(volume, symbol_info.volume_max))
            
            # Determine filling mode based on symbol
            filling_type = symbol_info.filling_mode
            
            # Try to use the best filling mode for this symbol
            if filling_type & 1:  # FOK
                filling_mode = mt5_lib.ORDER_FILLING_FOK
            elif filling_type & 2:  # IOC
                filling_mode = mt5_lib.ORDER_FILLING_IOC
            else:  # Return (default for forex)
                filling_mode = mt5_lib.ORDER_FILLING_RETURN
            
            request = {
                "action": mt5_lib.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": float(volume),
                "type": trade_type,
                "price": float(price),
                "sl": float(sl) if sl else 0.0,
                "tp": float(tp) if tp else 0.0,
                "deviation": 20,
                "magic": 234000,
                "comment": comment,
                "type_time": mt5_lib.ORDER_TIME_GTC,
                "type_filling": filling_mode,
            }
            
            print(f"Using filling mode: {filling_mode}")
            
            # Send order
            print(f"\n{'='*60}")
            print(f"SENDING ORDER TO MT5")
            print(f"{'='*60}")
            print(f"Symbol: {symbol}")
            print(f"Type: {order_type.upper()}")
            print(f"Volume: {volume}")
            print(f"Price: {price:.5f}")
            print(f"SL: {sl:.5f if sl else 0.0}")
            print(f"TP: {tp:.5f if tp else 0.0}")
            print(f"Filling Mode: {filling_mode}")
            print(f"{'='*60}\n")
            
            result = mt5_lib.order_send(request)
            
            if result is None:
                print("❌ ERROR: Order send returned None")
                print("Possible causes:")
                print("1. MT5 terminal not running")
                print("2. AutoTrading disabled in MT5")
                print("3. Connection lost")
                return None
            
            if result.retcode != mt5_lib.TRADE_RETCODE_DONE:
                print(f"❌ ORDER FAILED")
                print(f"Return Code: {result.retcode}")
                print(f"Comment: {result.comment}")
                print(f"\nCommon issues:")
                if result.retcode == 10004:
                    print("- Requote: Price changed, try again")
                elif result.retcode == 10006:
                    print("- Request rejected: Check if trading is allowed")
                elif result.retcode == 10014:
                    print("- Invalid volume: Check lot size")
                elif result.retcode == 10015:
                    print("- Invalid price: Check SL/TP levels")
                elif result.retcode == 10016:
                    print("- Invalid stops: SL/TP too close to price")
                elif result.retcode == 10019:
                    print("- Not enough money: Insufficient margin")
                elif result.retcode == 10030:
                    print("- Unsupported filling mode: Try different mode")
                return None
            
            print(f"✅ ORDER PLACED SUCCESSFULLY")
            print(f"Order ID: {result.order}")
            print(f"Deal ID: {result.deal}")
            print(f"Volume: {result.volume}")
            return result
            
        except Exception as e:
            print(f"Order execution error: {str(e)}")
            return None
    
    def get_open_positions(self):
        """Get all open positions."""
        if not MT5_AVAILABLE:
            return []
            
        if not self.connected:
            if not self.connect():
                return []
        
        try:
            import metatrader5 as mt5_lib
            
            positions = mt5_lib.positions_get()
            
            if positions is None or len(positions) == 0:
                return []
            
            positions_list = []
            for pos in positions:
                positions_list.append({
                    'ticket': int(pos.ticket),
                    'symbol': pos.symbol,
                    'type': 'buy' if pos.type == 0 else 'sell',  # 0 = buy, 1 = sell
                    'volume': float(pos.volume),
                    'price_open': float(pos.price_open),
                    'price_current': float(pos.price_current),
                    'sl': float(pos.sl),
                    'tp': float(pos.tp),
                    'profit': float(pos.profit),
                    'time': datetime.fromtimestamp(pos.time).isoformat()
                })
            
            return positions_list
            
        except Exception as e:
            print(f"Error getting positions: {str(e)}")
            return []
    
    def close_position(self, ticket):
        """Close a position by ticket number."""
        if not MT5_AVAILABLE:
            print("MT5 not available")
            return None
            
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            import metatrader5 as mt5_lib
            
            position = mt5_lib.positions_get(ticket=ticket)
            
            if position is None or len(position) == 0:
                print(f"Position {ticket} not found")
                return None
            
            position = position[0]
            
            # Prepare close request
            symbol = position.symbol
            volume = position.volume
            
            # Get current price
            tick = mt5_lib.symbol_info_tick(symbol)
            if tick is None:
                print(f"Failed to get tick for {symbol}")
                return None
            
            # Opposite direction to close
            if position.type == 0:  # Buy position
                trade_type = mt5_lib.ORDER_TYPE_SELL
                price = tick.bid
            else:  # Sell position
                trade_type = mt5_lib.ORDER_TYPE_BUY
                price = tick.ask
            
            print(f"\nClosing position:")
            print(f"  Ticket: {ticket}")
            print(f"  Symbol: {symbol}")
            print(f"  Volume: {volume}")
            print(f"  Type: {'SELL (closing BUY)' if position.type == 0 else 'BUY (closing SELL)'}")
            print(f"  Price: {price}")
            
            # Get symbol info for filling mode
            symbol_info = mt5_lib.symbol_info(symbol)
            if symbol_info:
                filling_type = symbol_info.filling_mode
                if filling_type & 1:
                    filling_mode = mt5_lib.ORDER_FILLING_FOK
                elif filling_type & 2:
                    filling_mode = mt5_lib.ORDER_FILLING_IOC
                else:
                    filling_mode = mt5_lib.ORDER_FILLING_RETURN
            else:
                filling_mode = mt5_lib.ORDER_FILLING_RETURN
            
            request = {
                "action": mt5_lib.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": float(volume),
                "type": trade_type,
                "position": int(ticket),
                "price": float(price),
                "deviation": 20,
                "magic": 234000,
                "comment": "Close by AI Trader",
                "type_time": mt5_lib.ORDER_TIME_GTC,
                "type_filling": filling_mode,
            }
            
            print(f"Using filling mode: {filling_mode}")
            
            print(f"Sending close request...")
            result = mt5_lib.order_send(request)
            
            if result is None:
                print("✗ Close order returned None")
                return None
            
            print(f"Result retcode: {result.retcode}")
            print(f"Result comment: {result.comment}")
            
            if result.retcode != mt5_lib.TRADE_RETCODE_DONE:
                print(f"✗ Failed to close position: {result.retcode} - {result.comment}")
                print(f"  Possible reasons:")
                print(f"  - Position already closed")
                print(f"  - Invalid ticket number")
                print(f"  - Market closed")
                print(f"  - Connection issue")
                return None
            
            print(f"✓ Position {ticket} closed successfully")
            return result
            
        except Exception as e:
            print(f"Error closing position: {str(e)}")
            return None
    
    def get_account_info(self):
        """Get account information."""
        if not self.connected:
            self.connect()
        
        account = mt5.account_info()
        
        if account is None:
            return None
        
        return {
            'balance': account.balance,
            'equity': account.equity,
            'margin': account.margin,
            'free_margin': account.margin_free,
            'profit': account.profit,
            'currency': account.currency,
            'leverage': account.leverage,
            'name': account.name,
            'server': account.server,
            'company': account.company
        }
