"""Unified broker manager - supports MT5, Deriv, and OANDA."""

from mt5_connector import MT5Connector
from deriv_connector import DerivConnector
from oanda_connector import OandaConnector
from mt5_brokers import MT5_BROKERS, get_broker_info, get_brokers_by_country


class BrokerManager:
    """
    Unified interface for multiple brokers.
    
    Supported brokers:
    - MT5 (Windows only, local trading)
    - Deriv (Cloud, available in Kenya)
    - OANDA (Cloud, not available in Kenya)
    """
    
    def __init__(self, broker_type='deriv', **credentials):
        """
        Initialize broker connection.
        
        Args:
            broker_type: 'mt5', 'deriv', or 'oanda'
            **credentials: Broker-specific credentials
            
        Examples:
            # MT5
            broker = BrokerManager('mt5', 
                login='12345', 
                password='pass', 
                server='Broker-Demo')
            
            # Deriv
            broker = BrokerManager('deriv', 
                api_token='your_token', 
                demo=True)
            
            # OANDA
            broker = BrokerManager('oanda', 
                api_key='your_key', 
                account_id='123-456', 
                practice=True)
        """
        self.broker_type = broker_type.lower()
        self.connector = None
        
        if self.broker_type == 'mt5':
            self.connector = MT5Connector()
            self.connector.login = credentials.get('login')
            self.connector.password = credentials.get('password')
            self.connector.server = credentials.get('server')
            self.connector.path = credentials.get('path')
            
        elif self.broker_type == 'deriv':
            self.connector = DerivConnector(
                api_token=credentials.get('api_token'),
                app_id=credentials.get('app_id', '1089'),
                demo=credentials.get('demo', True)
            )
            
        elif self.broker_type == 'oanda':
            self.connector = OandaConnector(
                api_key=credentials.get('api_key'),
                account_id=credentials.get('account_id'),
                practice=credentials.get('practice', True)
            )
            
        else:
            raise ValueError(f"Unsupported broker: {broker_type}")
    
    def connect(self):
        """Connect to broker."""
        return self.connector.connect()
    
    def disconnect(self):
        """Disconnect from broker."""
        return self.connector.disconnect()
    
    def get_account_info(self):
        """Get account information."""
        return self.connector.get_account_info()
    
    def get_historical_data(self, symbol, timeframe='M5', bars=500):
        """Get historical price data."""
        return self.connector.get_historical_data(symbol, timeframe, bars)
    
    def place_order(self, symbol, order_type, volume, sl=None, tp=None, comment="AI Trader"):
        """Place a market order."""
        return self.connector.place_order(symbol, order_type, volume, sl, tp, comment)
    
    def get_open_positions(self):
        """Get all open positions."""
        return self.connector.get_open_positions()
    
    def close_position(self, ticket):
        """Close a specific position."""
        return self.connector.close_position(ticket)
    
    def get_current_price(self, symbol):
        """Get current bid/ask price."""
        return self.connector.get_current_price(symbol)
    
    @property
    def connected(self):
        """Check if connected."""
        return self.connector.connected
    
    def get_broker_info(self):
        """Get broker information."""
        return {
            'type': self.broker_type,
            'name': self._get_broker_name(),
            'cloud_compatible': self.broker_type in ['deriv', 'oanda'],
            'available_in_kenya': self.broker_type in ['mt5', 'deriv'],
            'requires_installation': self.broker_type == 'mt5'
        }
    
    def _get_broker_name(self):
        """Get friendly broker name."""
        names = {
            'mt5': 'MetaTrader 5',
            'deriv': 'Deriv',
            'oanda': 'OANDA'
        }
        return names.get(self.broker_type, 'Unknown')


# Broker availability by country
BROKER_AVAILABILITY = {
    'kenya': ['mt5', 'deriv'],
    'nigeria': ['mt5', 'deriv', 'oanda'],
    'south_africa': ['mt5', 'deriv', 'oanda'],
    'usa': ['oanda'],  # MT5 restricted in USA
    'uk': ['mt5', 'deriv', 'oanda'],
    'default': ['mt5', 'deriv', 'oanda']
}


def get_available_brokers(country='default'):
    """
    Get list of available brokers for a country.
    
    Args:
        country: Country code (lowercase)
    
    Returns:
        List of available broker types
    """
    return BROKER_AVAILABILITY.get(country.lower(), BROKER_AVAILABILITY['default'])


def get_mt5_broker_presets():
    """Get MT5 broker presets."""
    return MT5_BROKERS


def get_broker_details():
    """Get details about all supported brokers."""
    details = {
        'mt5': {
            'name': 'MetaTrader 5',
            'description': 'Most popular forex platform',
            'pros': [
                'Widely supported by brokers',
                'Advanced charting',
                'Large community'
            ],
            'cons': [
                'Windows only',
                'Requires installation',
                'Not cloud-compatible'
            ],
            'available_in': ['Kenya', 'Nigeria', 'South Africa', 'Most countries'],
            'signup_url': 'https://www.metatrader5.com/',
            'credentials_needed': ['Login', 'Password', 'Server'],
            'brokers': MT5_BROKERS
        },
        'deriv': {
            'name': 'Deriv',
            'description': 'Cloud-based trading platform',
            'pros': [
                'Available in Kenya',
                'Cloud-compatible',
                'Free demo account',
                'Synthetic indices',
                'No installation needed'
            ],
            'cons': [
                'Different from traditional forex',
                'Limited to Deriv markets'
            ],
            'available_in': ['Kenya', 'Nigeria', 'South Africa', '100+ countries'],
            'signup_url': 'https://deriv.com/',
            'credentials_needed': ['API Token']
        },
        'oanda': {
            'name': 'OANDA',
            'description': 'Professional forex broker',
            'pros': [
                'Cloud-compatible',
                'Excellent API',
                'Good documentation',
                'Free demo account'
            ],
            'cons': [
                'Not available in Kenya',
                'Not available in USA'
            ],
            'available_in': ['Nigeria', 'South Africa', 'UK', 'Most of Europe'],
            'signup_url': 'https://www.oanda.com/',
            'credentials_needed': ['API Key', 'Account ID']
        }
    }
