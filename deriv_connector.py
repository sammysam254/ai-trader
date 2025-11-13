"""Deriv API connector - Available in Kenya and most countries."""

import requests
import pandas as pd
from datetime import datetime
import json
import websocket
import threading
import time


class DerivConnector:
    """
    Connect to Deriv for cloud-based trading.
    
    Deriv is available in Kenya and supports:
    - Forex
    - Synthetic Indices
    - Commodities
    - No MT5 needed
    - Free demo account
    """
    
    def __init__(self, api_token, app_id="1089", demo=True):
        """
        Initialize Deriv connector.
        
        Args:
            api_token: Deriv API token
            app_id: Your app ID (default works for testing)
            demo: True for demo account, False for real
        """
        self.api_token = api_token
        self.app_id = app_id
        self.demo = demo
        self.connected = False
        
        # WebSocket connection
        self.ws_url = f"wss://ws.binaryws.com/websockets/v3?app_id={app_id}"
        self.ws = None
        self.ws_thread = None
        self.responses = {}
        
        # REST API (for some operations)
        self.base_url = "https://api.deriv.com"
    
    def connect(self):
        """Connect to Deriv via WebSocket."""
        try:
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )
            
            # Start WebSocket in background thread
            self.ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            self.ws_thread.start()
            
            # Wait for connection
            time.sleep(2)
            
            # Authorize
            self._send_request({
                "authorize": self.api_token
            })
            
            time.sleep(1)
            
            if self.connected:
                print("✓ Connected to Deriv successfully")
                return True
            else:
                print("✗ Failed to connect to Deriv")
                return False
                
        except Exception as e:
            print(f"✗ Connection error: {str(e)}")
            return False
    
    def _on_message(self, ws, message):
        """Handle WebSocket messages."""
        try:
            data = json.loads(message)
            print(f"Received message: {data}")
            
            # Handle authorization
            if 'authorize' in data:
                if 'error' not in data:
                    self.connected = True
                    print("✓ Authorized with Deriv")
                else:
                    print(f"✗ Authorization failed: {data['error']['message']}")
            
            # Store response for retrieval
            if 'req_id' in data:
                print(f"Storing response for req_id: {data['req_id']}")
                self.responses[data['req_id']] = data
                
        except Exception as e:
            print(f"Error handling message: {str(e)}")
    
    def _on_error(self, ws, error):
        """Handle WebSocket errors."""
        print(f"WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close."""
        self.connected = False
        print("WebSocket connection closed")
    
    def _on_open(self, ws):
        """Handle WebSocket open."""
        print("WebSocket connection opened")
    
    def _send_request(self, request, req_id=None):
        """Send request via WebSocket."""
        if req_id is None:
            req_id = str(int(time.time() * 1000))
        
        request['req_id'] = req_id
        self.ws.send(json.dumps(request))
        
        # Wait for response
        timeout = 10
        start = time.time()
        while req_id not in self.responses:
            if time.time() - start > timeout:
                return None
            time.sleep(0.1)
        
        return self.responses.pop(req_id)
    
    def disconnect(self):
        """Disconnect from Deriv."""
        if self.ws:
            self.ws.close()
        self.connected = False
    
    def get_account_info(self):
        """Get account information."""
        try:
            response = self._send_request({"balance": 1})
            
            if response and 'balance' in response:
                balance_data = response['balance']
                
                return {
                    'balance': float(balance_data['balance']),
                    'equity': float(balance_data['balance']),  # Deriv doesn't separate
                    'profit': 0.0,  # Calculate from open positions
                    'margin': 0.0,
                    'free_margin': float(balance_data['balance']),
                    'currency': balance_data['currency']
                }
            else:
                return None
                
        except Exception as e:
            print(f"Error getting account info: {str(e)}")
            return None
    
    def get_historical_data(self, symbol, timeframe='M5', bars=500):
        """
        Get historical price data.
        
        Args:
            symbol: Market symbol (e.g., 'frxEURUSD', 'R_50', 'R_100')
            timeframe: Candle interval (60, 300, 900, 3600, etc. in seconds)
            bars: Number of candles
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Convert timeframe to seconds
            timeframe_map = {
                'M1': 60, 'M5': 300, 'M15': 900, 'M30': 1800,
                'H1': 3600, 'H4': 14400, 'D1': 86400
            }
            granularity = timeframe_map.get(timeframe, 300)
            
            # Convert symbol to Deriv format
            # Deriv uses different symbols than MT5
            symbol_map = {
                'EURUSD': 'frxEURUSD',
                'GBPUSD': 'frxGBPUSD', 
                'USDJPY': 'frxUSDJPY',
                'AUDUSD': 'frxAUDUSD',
                'USDCAD': 'frxUSDCAD',
                'NZDUSD': 'frxNZDUSD',
                'XAUUSD': 'frxXAUUSD'
            }
            
            deriv_symbol = symbol_map.get(symbol, f"frx{symbol}")
            print(f"Converting {symbol} to {deriv_symbol}")
            
            # Request candles
            request_data = {
                "ticks_history": deriv_symbol,
                "adjust_start_time": 1,
                "count": bars,
                "end": "latest",
                "start": 1,
                "style": "candles",
                "granularity": granularity
            }
            print(f"Requesting data: {request_data}")
            
            response = self._send_request(request_data)
            
            print(f"Response: {response}")
            
            if not response or 'candles' not in response:
                print(f"Failed to get data for {deriv_symbol}")
                if response and 'error' in response:
                    print(f"Error from Deriv: {response['error']}")
                return None
            
            candles = response['candles']
            
            # Convert to DataFrame
            df_data = []
            for candle in candles:
                df_data.append({
                    'time': pd.to_datetime(candle['epoch'], unit='s'),
                    'open': float(candle['open']),
                    'high': float(candle['high']),
                    'low': float(candle['low']),
                    'close': float(candle['close']),
                    'volume': 0  # Deriv doesn't provide volume
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('time', inplace=True)
            
            return df
            
        except Exception as e:
            print(f"Error getting historical data: {str(e)}")
            return None
    
    def place_order(self, symbol, order_type, volume, sl=None, tp=None, comment="AI Trader"):
        """
        Place a market order.
        
        Args:
            symbol: Market symbol
            order_type: 'buy' or 'sell'
            volume: Position size (stake amount in USD for Deriv)
            sl: Stop loss price
            tp: Take profit price
            comment: Order comment
        
        Returns:
            Order result dict or None
        """
        try:
            # Convert symbol using the same mapping
            symbol_map = {
                'EURUSD': 'frxEURUSD',
                'GBPUSD': 'frxGBPUSD', 
                'USDJPY': 'frxUSDJPY',
                'AUDUSD': 'frxAUDUSD',
                'USDCAD': 'frxUSDCAD',
                'NZDUSD': 'frxNZDUSD',
                'XAUUSD': 'frxXAUUSD'
            }
            
            deriv_symbol = symbol_map.get(symbol, f"frx{symbol}")
            
            # Deriv uses stake amount, not lots
            stake = volume * 10  # Convert lots to USD stake
            
            print(f"\n{'='*60}")
            print(f"SENDING ORDER TO DERIV")
            print(f"{'='*60}")
            print(f"Symbol: {deriv_symbol}")
            print(f"Type: {order_type.upper()}")
            print(f"Stake: ${stake}")
            print(f"SL: {sl if sl else 'None'}")
            print(f"TP: {tp if tp else 'None'}")
            print(f"{'='*60}\n")
            
            # Place order
            request = {
                "buy": 1,
                "price": stake,
                "parameters": {
                    "contract_type": "CALL" if order_type.lower() == 'buy' else "PUT",
                    "symbol": deriv_symbol,
                    "duration": 5,  # 5 minutes
                    "duration_unit": "m",
                    "basis": "stake",
                    "amount": stake
                }
            }
            
            response = self._send_request(request)
            
            if response and 'buy' in response:
                result = response['buy']
                print("✅ ORDER PLACED SUCCESSFULLY")
                print(f"Contract ID: {result['contract_id']}")
                print(f"Stake: ${result['buy_price']}")
                
                # Return in MT5-like format
                class OrderResult:
                    def __init__(self, data):
                        self.order = data['contract_id']
                        self.deal = data['contract_id']
                        self.volume = volume
                
                return OrderResult(result)
            else:
                print(f"❌ ORDER FAILED")
                if response and 'error' in response:
                    print(f"Error: {response['error']['message']}")
                return None
                
        except Exception as e:
            print(f"Order execution error: {str(e)}")
            return None
    
    def get_open_positions(self):
        """Get all open positions."""
        try:
            response = self._send_request({"portfolio": 1})
            
            if not response or 'portfolio' not in response:
                return []
            
            contracts = response['portfolio']['contracts']
            
            positions = []
            for contract in contracts:
                positions.append({
                    'ticket': contract['contract_id'],
                    'symbol': contract['symbol'],
                    'type': 'buy' if contract['contract_type'] == 'CALL' else 'sell',
                    'volume': float(contract['buy_price']) / 10,  # Convert back to lots
                    'price_open': float(contract['buy_price']),
                    'price_current': float(contract.get('bid_price', contract['buy_price'])),
                    'sl': 0,
                    'tp': 0,
                    'profit': float(contract.get('profit', 0)),
                    'time': contract['purchase_time']
                })
            
            return positions
            
        except Exception as e:
            print(f"Error getting positions: {str(e)}")
            return []
    
    def close_position(self, ticket):
        """Close a specific position."""
        try:
            response = self._send_request({
                "sell": ticket,
                "price": 0  # Market price
            })
            
            if response and 'sell' in response:
                print(f"✓ Position {ticket} closed successfully")
                return True
            else:
                print(f"✗ Failed to close position")
                if response and 'error' in response:
                    print(f"Error: {response['error']['message']}")
                return False
                
        except Exception as e:
            print(f"Error closing position: {str(e)}")
            return False
    
    def get_current_price(self, symbol):
        """Get current price."""
        try:
            # Convert symbol
            if symbol.startswith('frx'):
                deriv_symbol = symbol
            elif len(symbol) == 6:
                deriv_symbol = f"frx{symbol}"
            else:
                deriv_symbol = symbol
            
            response = self._send_request({
                "ticks": deriv_symbol,
                "subscribe": 0
            })
            
            if response and 'tick' in response:
                tick = response['tick']
                price = float(tick['quote'])
                
                return {
                    'bid': price,
                    'ask': price * 1.0001,  # Approximate spread
                    'time': datetime.now()
                }
            else:
                return None
                
        except Exception as e:
            print(f"Error getting price: {str(e)}")
            return None
