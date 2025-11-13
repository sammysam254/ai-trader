"""OANDA API connector for cloud-based multi-user trading."""

import requests
import pandas as pd
from datetime import datetime
import time


class OandaConnector:
    """Connect to OANDA for cloud-based trading (no MT5 needed)."""
    
    def __init__(self, api_key, account_id, practice=True):
        """
        Initialize OANDA connector.
        
        Args:
            api_key: OANDA API key
            account_id: OANDA account ID
            practice: True for demo, False for live
        """
        self.api_key = api_key
        self.account_id = account_id
        self.connected = False
        
        # Use practice or live API
        if practice:
            self.base_url = "https://api-fxpractice.oanda.com"
        else:
            self.base_url = "https://api-fxtrade.oanda.com"
        
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def connect(self):
        """Test connection to OANDA."""
        try:
            response = requests.get(
                f"{self.base_url}/v3/accounts/{self.account_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.connected = True
                print("✓ Connected to OANDA successfully")
                return True
            else:
                print(f"✗ OANDA connection failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Connection error: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect (just set flag)."""
        self.connected = False
    
    def get_account_info(self):
        """Get account information."""
        try:
            response = requests.get(
                f"{self.base_url}/v3/accounts/{self.account_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                account = data['account']
                
                return {
                    'balance': float(account['balance']),
                    'equity': float(account['NAV']),
                    'profit': float(account['unrealizedPL']),
                    'margin': float(account.get('marginUsed', 0)),
                    'free_margin': float(account.get('marginAvailable', 0)),
                    'currency': account['currency']
                }
            else:
                print(f"Failed to get account info: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting account info: {str(e)}")
            return None
    
    def get_historical_data(self, symbol, timeframe='M5', bars=500):
        """
        Get historical price data.
        
        Args:
            symbol: Instrument (e.g., 'EUR_USD')
            timeframe: Candle granularity (M5, M15, H1, etc.)
            bars: Number of candles
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Convert MT5 symbols to OANDA format
            oanda_symbol = symbol.replace('/', '_')
            if '_' not in oanda_symbol and len(oanda_symbol) == 6:
                oanda_symbol = f"{oanda_symbol[:3]}_{oanda_symbol[3:]}"
            
            # Convert timeframe
            granularity_map = {
                'M1': 'M1', 'M5': 'M5', 'M15': 'M15', 'M30': 'M30',
                'H1': 'H1', 'H4': 'H4', 'D1': 'D', 'W1': 'W'
            }
            granularity = granularity_map.get(timeframe, 'M5')
            
            response = requests.get(
                f"{self.base_url}/v3/instruments/{oanda_symbol}/candles",
                headers=self.headers,
                params={
                    'count': bars,
                    'granularity': granularity,
                    'price': 'M'  # Mid prices
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"Failed to get data: {response.status_code}")
                return None
            
            data = response.json()
            candles = data['candles']
            
            # Convert to DataFrame
            df_data = []
            for candle in candles:
                if candle['complete']:
                    df_data.append({
                        'time': pd.to_datetime(candle['time']),
                        'open': float(candle['mid']['o']),
                        'high': float(candle['mid']['h']),
                        'low': float(candle['mid']['l']),
                        'close': float(candle['mid']['c']),
                        'volume': int(candle['volume'])
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
            symbol: Instrument (e.g., 'EURUSD' or 'EUR_USD')
            order_type: 'buy' or 'sell'
            volume: Position size in lots (OANDA uses units)
            sl: Stop loss price
            tp: Take profit price
            comment: Order comment
        
        Returns:
            Order result dict or None
        """
        try:
            # Convert symbol to OANDA format
            oanda_symbol = symbol.replace('/', '_')
            if '_' not in oanda_symbol and len(oanda_symbol) == 6:
                oanda_symbol = f"{oanda_symbol[:3]}_{oanda_symbol[3:]}"
            
            # Convert lots to units (1 lot = 100,000 units for forex)
            units = int(volume * 100000)
            if order_type.lower() == 'sell':
                units = -units
            
            # Build order request
            order_data = {
                "order": {
                    "instrument": oanda_symbol,
                    "units": str(units),
                    "type": "MARKET",
                    "timeInForce": "FOK",
                    "positionFill": "DEFAULT"
                }
            }
            
            # Add stop loss
            if sl:
                order_data["order"]["stopLossOnFill"] = {
                    "price": str(round(sl, 5))
                }
            
            # Add take profit
            if tp:
                order_data["order"]["takeProfitOnFill"] = {
                    "price": str(round(tp, 5))
                }
            
            print(f"\n{'='*60}")
            print(f"SENDING ORDER TO OANDA")
            print(f"{'='*60}")
            print(f"Symbol: {oanda_symbol}")
            print(f"Type: {order_type.upper()}")
            print(f"Units: {units} ({volume} lots)")
            print(f"SL: {sl if sl else 'None'}")
            print(f"TP: {tp if tp else 'None'}")
            print(f"{'='*60}\n")
            
            response = requests.post(
                f"{self.base_url}/v3/accounts/{self.account_id}/orders",
                headers=self.headers,
                json=order_data,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                print("✅ ORDER PLACED SUCCESSFULLY")
                print(f"Order ID: {result['orderFillTransaction']['id']}")
                print(f"Trade ID: {result['orderFillTransaction']['tradeOpened']['tradeID']}")
                
                # Return in MT5-like format for compatibility
                class OrderResult:
                    def __init__(self, data):
                        self.order = data['orderFillTransaction']['id']
                        self.deal = data['orderFillTransaction']['tradeOpened']['tradeID']
                        self.volume = volume
                
                return OrderResult(result)
            else:
                print(f"❌ ORDER FAILED: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Order execution error: {str(e)}")
            return None
    
    def get_open_positions(self):
        """Get all open positions."""
        try:
            response = requests.get(
                f"{self.base_url}/v3/accounts/{self.account_id}/openTrades",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            trades = data.get('trades', [])
            
            positions = []
            for trade in trades:
                # Get current price
                symbol = trade['instrument']
                current_price = float(trade['price'])
                
                # Calculate P&L
                unrealized_pl = float(trade['unrealizedPL'])
                
                positions.append({
                    'ticket': trade['id'],
                    'symbol': symbol.replace('_', ''),
                    'type': 'buy' if float(trade['currentUnits']) > 0 else 'sell',
                    'volume': abs(float(trade['currentUnits'])) / 100000,
                    'price_open': float(trade['price']),
                    'price_current': current_price,
                    'sl': float(trade.get('stopLossOrder', {}).get('price', 0)),
                    'tp': float(trade.get('takeProfitOrder', {}).get('price', 0)),
                    'profit': unrealized_pl,
                    'time': trade['openTime']
                })
            
            return positions
            
        except Exception as e:
            print(f"Error getting positions: {str(e)}")
            return []
    
    def close_position(self, ticket):
        """Close a specific position."""
        try:
            # OANDA uses trade ID directly
            response = requests.put(
                f"{self.base_url}/v3/accounts/{self.account_id}/trades/{ticket}/close",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✓ Position {ticket} closed successfully")
                return True
            else:
                print(f"✗ Failed to close position: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error closing position: {str(e)}")
            return False
    
    def get_current_price(self, symbol):
        """Get current bid/ask price."""
        try:
            # Convert symbol
            oanda_symbol = symbol.replace('/', '_')
            if '_' not in oanda_symbol and len(oanda_symbol) == 6:
                oanda_symbol = f"{oanda_symbol[:3]}_{oanda_symbol[3:]}"
            
            response = requests.get(
                f"{self.base_url}/v3/accounts/{self.account_id}/pricing",
                headers=self.headers,
                params={'instruments': oanda_symbol},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                price = data['prices'][0]
                
                return {
                    'bid': float(price['bids'][0]['price']),
                    'ask': float(price['asks'][0]['price']),
                    'time': datetime.now()
                }
            else:
                return None
                
        except Exception as e:
            print(f"Error getting price: {str(e)}")
            return None
