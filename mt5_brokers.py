"""MT5 Broker presets for popular brokers in Kenya and worldwide."""

# Popular MT5 brokers with their server configurations
MT5_BROKERS = {
    'exness': {
        'name': 'Exness',
        'description': 'Popular in Kenya, low spreads, instant withdrawals',
        'servers': [
            'Exness-MT5Real',
            'Exness-MT5Real2',
            'Exness-MT5Real3',
            'Exness-MT5Trial',
            'Exness-MT5Trial2'
        ],
        'demo_server': 'Exness-MT5Trial',
        'real_server': 'Exness-MT5Real',
        'website': 'https://www.exness.com/',
        'min_deposit': 1,
        'currency': 'USD',
        'available_in': ['Kenya', 'Nigeria', 'South Africa', 'Most countries'],
        'payment_methods': ['M-Pesa', 'Bank transfer', 'Cards', 'Skrill', 'Neteller'],
        'features': [
            'Instant withdrawals',
            'Low spreads from 0.0 pips',
            '$1 minimum deposit',
            'M-Pesa support',
            'Unlimited leverage',
            'No swap on some accounts'
        ]
    },
    'hfm': {
        'name': 'HFM (HotForex)',
        'description': 'Trusted broker, good for beginners',
        'servers': [
            'HFMarkets-Demo',
            'HFMarkets-Real',
            'HFMarkets-Real 2',
            'HFMarkets-Real 3'
        ],
        'demo_server': 'HFMarkets-Demo',
        'real_server': 'HFMarkets-Real',
        'website': 'https://www.hfm.com/',
        'min_deposit': 5,
        'currency': 'USD',
        'available_in': ['Kenya', 'Nigeria', 'South Africa', 'Most countries'],
        'payment_methods': ['M-Pesa', 'Bank transfer', 'Cards', 'Skrill', 'Neteller'],
        'features': [
            'Regulated by multiple authorities',
            'Good customer support',
            '$5 minimum deposit',
            'M-Pesa deposits',
            'Copy trading available',
            'Educational resources'
        ]
    },
    'windsor': {
        'name': 'Windsor Brokers',
        'description': 'Established broker, good reputation',
        'servers': [
            'WindsorBrokers-Demo',
            'WindsorBrokers-Live',
            'WindsorBrokers-Live2'
        ],
        'demo_server': 'WindsorBrokers-Demo',
        'real_server': 'WindsorBrokers-Live',
        'website': 'https://www.windsorbrokers.com/',
        'min_deposit': 50,
        'currency': 'USD',
        'available_in': ['Kenya', 'Nigeria', 'South Africa', 'Europe', 'Middle East'],
        'payment_methods': ['Bank transfer', 'Cards', 'Skrill', 'Neteller'],
        'features': [
            'Regulated in Cyprus',
            'Over 50 years experience',
            'Negative balance protection',
            'Free VPS for active traders',
            'Multiple account types',
            'Good for serious traders'
        ]
    },
    'xm': {
        'name': 'XM',
        'description': 'Very popular, great for beginners',
        'servers': [
            'XMGlobal-MT5',
            'XMGlobal-MT5 2',
            'XMGlobal-MT5 3',
            'XMGlobal-Demo'
        ],
        'demo_server': 'XMGlobal-Demo',
        'real_server': 'XMGlobal-MT5',
        'website': 'https://www.xm.com/',
        'min_deposit': 5,
        'currency': 'USD',
        'available_in': ['Kenya', 'Nigeria', 'Most countries'],
        'payment_methods': ['Bank transfer', 'Cards', 'Skrill', 'Neteller'],
        'features': [
            'No deposit bonuses',
            'Great education',
            '$5 minimum deposit',
            'Excellent support',
            'Webinars and seminars',
            'Loyalty program'
        ]
    },
    'fbs': {
        'name': 'FBS',
        'description': 'Low minimum deposit, good for starters',
        'servers': [
            'FBS-Demo',
            'FBS-Real',
            'FBS-Real-2',
            'FBS-Real-3'
        ],
        'demo_server': 'FBS-Demo',
        'real_server': 'FBS-Real',
        'website': 'https://fbs.com/',
        'min_deposit': 1,
        'currency': 'USD',
        'available_in': ['Kenya', 'Nigeria', 'South Africa', 'Most countries'],
        'payment_methods': ['M-Pesa', 'Bank transfer', 'Cards', 'Perfect Money'],
        'features': [
            '$1 minimum deposit',
            'M-Pesa deposits',
            'High leverage up to 1:3000',
            'Cashback program',
            'Copy trading',
            'Mobile trading app'
        ]
    },
    'ic_markets': {
        'name': 'IC Markets',
        'description': 'Professional broker, low spreads',
        'servers': [
            'ICMarketsSC-Demo',
            'ICMarketsSC-MT5',
            'ICMarketsSC-MT5-2'
        ],
        'demo_server': 'ICMarketsSC-Demo',
        'real_server': 'ICMarketsSC-MT5',
        'website': 'https://www.icmarkets.com/',
        'min_deposit': 200,
        'currency': 'USD',
        'available_in': ['Kenya', 'Nigeria', 'South Africa', 'Most countries'],
        'payment_methods': ['Bank transfer', 'Cards', 'Skrill', 'Neteller'],
        'features': [
            'Lowest spreads (from 0.0 pips)',
            'Fast execution',
            'Professional platform',
            'cTrader available',
            'Good for scalping',
            'High volume traders'
        ]
    },
    'tickmill': {
        'name': 'Tickmill',
        'description': 'Low cost trading, good execution',
        'servers': [
            'Tickmill-Demo',
            'Tickmill-Live',
            'Tickmill-Live02'
        ],
        'demo_server': 'Tickmill-Demo',
        'real_server': 'Tickmill-Live',
        'website': 'https://www.tickmill.com/',
        'min_deposit': 100,
        'currency': 'USD',
        'available_in': ['Kenya', 'Nigeria', 'South Africa', 'Europe'],
        'payment_methods': ['Bank transfer', 'Cards', 'Skrill', 'Neteller'],
        'features': [
            'Regulated in UK and Cyprus',
            'Low commissions',
            'Fast execution',
            'Good for scalpers',
            'VPS available',
            'Professional service'
        ]
    },
    'other': {
        'name': 'Other MT5 Broker',
        'description': 'Use any MT5 broker',
        'servers': [],
        'demo_server': '',
        'real_server': '',
        'website': '',
        'min_deposit': 0,
        'currency': 'USD',
        'available_in': ['Worldwide'],
        'payment_methods': ['Varies by broker'],
        'features': [
            'Enter your broker details manually',
            'Works with any MT5 broker',
            'Get server name from your broker'
        ]
    }
}


def get_broker_list():
    """Get list of all supported MT5 brokers."""
    return list(MT5_BROKERS.keys())


def get_broker_info(broker_key):
    """Get information about a specific broker."""
    return MT5_BROKERS.get(broker_key.lower())


def get_brokers_by_country(country='kenya'):
    """Get brokers available in a specific country."""
    country = country.lower()
    available = []
    
    for key, broker in MT5_BROKERS.items():
        if key == 'other':
            continue
        
        # Check if country is in available list
        available_countries = [c.lower() for c in broker['available_in']]
        if country in available_countries or 'most countries' in available_countries or 'worldwide' in available_countries:
            available.append(key)
    
    return available


def get_recommended_brokers(country='kenya', min_deposit=None):
    """Get recommended brokers based on criteria."""
    available = get_brokers_by_country(country)
    
    if min_deposit is not None:
        # Filter by minimum deposit
        available = [
            key for key in available 
            if MT5_BROKERS[key]['min_deposit'] <= min_deposit
        ]
    
    # Sort by minimum deposit (lowest first)
    available.sort(key=lambda x: MT5_BROKERS[x]['min_deposit'])
    
    return available


def supports_mpesa(broker_key):
    """Check if broker supports M-Pesa."""
    broker = MT5_BROKERS.get(broker_key.lower())
    if not broker:
        return False
    
    return 'M-Pesa' in broker['payment_methods'] or 'm-pesa' in [p.lower() for p in broker['payment_methods']]


# Kenya-specific recommendations
KENYA_RECOMMENDED = ['exness', 'hfm', 'fbs', 'xm']

# Beginner-friendly brokers (low minimum deposit)
BEGINNER_FRIENDLY = ['exness', 'fbs', 'hfm', 'xm']

# Professional brokers (better for experienced traders)
PROFESSIONAL = ['ic_markets', 'tickmill', 'windsor']

# M-Pesa supported brokers
MPESA_SUPPORTED = ['exness', 'hfm', 'fbs']
