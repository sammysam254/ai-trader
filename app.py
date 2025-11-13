"""Flask web application for AI Forex Trader."""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import threading
import time

from mt5_connector import MT5Connector
from indicators import IndicatorEngine
from signal_generator import SignalGenerator
from ml_model import TradingModel
from risk_manager import RiskManager
from backtester import Backtester
import config

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'change-this-secret-key')
CORS(app)

# Global variables
mt5 = MT5Connector()
ml_model = TradingModel()
risk_manager = None
trading_active = False
current_signals = {}
account_info = {}


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/api/connect', methods=['POST'])
def connect_mt5():
    """Connect to MT5 with provided credentials."""
    global mt5, risk_manager, account_info
    
    try:
        # Get credentials from request
        data = request.json
        login = data.get('login')
        password = data.get('password')
        server = data.get('server')
        path = data.get('path', 'C:\\Program Files\\MetaTrader 5\\terminal64.exe')
        
        # Validate inputs
        if not login or not password or not server:
            return jsonify({
                'success': False,
                'message': 'Missing required credentials'
            }), 400
        
        # Update MT5 connector with new credentials
        mt5.login = login
        mt5.password = password
        mt5.server = server
        mt5.path = path
        
        # Attempt connection
        print(f"Attempting MT5 connection - Login: {login}, Server: {server}")
        
        if mt5.connect():
            account_info = mt5.get_account_info()
            
            if not account_info:
                return jsonify({
                    'success': False,
                    'message': 'Connected but failed to get account info. Please try again.'
                }), 400
            
            risk_manager = RiskManager(account_info['balance'])
            
            # Detect account type (Demo or Real)
            account_type = detect_account_type(server, account_info)
            
            print(f"Successfully connected to {account_type} account")
            
            return jsonify({
                'success': True,
                'message': f'Connected to MT5 successfully ({account_type} account)',
                'account': account_info,
                'account_type': account_type
            })
        else:
            error_msg = 'Failed to connect to MT5. Please check:\n'
            error_msg += '1. MetaTrader 5 is installed\n'
            error_msg += '2. Login number is correct (numbers only)\n'
            error_msg += '3. Password is correct\n'
            error_msg += '4. Server name matches exactly (e.g., "ICMarkets-Demo")\n'
            error_msg += '5. Your account is active'
            
            print(f"MT5 connection failed for login: {login}, server: {server}")
            
            return jsonify({
                'success': False,
                'message': error_msg
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Connection error: {str(e)}'
        }), 500


def detect_account_type(server, account_info):
    """Detect if account is Demo or Real based on server name and account info."""
    server_lower = server.lower()
    
    # Check server name for demo indicators
    demo_keywords = ['demo', 'test', 'practice', 'trial', 'contest']
    if any(keyword in server_lower for keyword in demo_keywords):
        return 'DEMO'
    
    # Check account name/company for demo indicators
    if account_info:
        name = account_info.get('name', '').lower()
        company = account_info.get('company', '').lower()
        
        if any(keyword in name for keyword in demo_keywords):
            return 'DEMO'
        if any(keyword in company for keyword in demo_keywords):
            return 'DEMO'
    
    # If no demo indicators found, assume it's real
    return 'REAL'


@app.route('/api/disconnect', methods=['POST'])
def disconnect_mt5():
    """Disconnect from MT5."""
    global mt5, trading_active
    
    trading_active = False
    mt5.disconnect()
    
    return jsonify({
        'success': True,
        'message': 'Disconnected from MT5'
    })


@app.route('/api/account')
def get_account():
    """Get account information."""
    global mt5, account_info
    
    if not mt5.connected:
        return jsonify({'error': 'Not connected to MT5'}), 400
    
    account_info = mt5.get_account_info()
    return jsonify(account_info)


@app.route('/api/positions')
def get_positions():
    """Get open positions."""
    global mt5
    
    if not mt5.connected:
        return jsonify({'error': 'Not connected to MT5'}), 400
    
    positions = mt5.get_open_positions()
    return jsonify(positions)


@app.route('/api/close-position/<int:ticket>', methods=['POST'])
def close_position(ticket):
    """Close a specific position."""
    global mt5
    
    if not mt5.connected:
        return jsonify({'error': 'Not connected to MT5'}), 400
    
    result = mt5.close_position(ticket)
    
    if result:
        return jsonify({
            'success': True,
            'message': f'Position {ticket} closed'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to close position'
        }), 400


@app.route('/api/analyze', methods=['POST'])
def analyze_pair():
    """Analyze a currency pair and generate signals."""
    global mt5, ml_model
    
    data = request.json
    symbol = data.get('symbol', 'EURUSD')
    timeframe = data.get('timeframe', 'H1')
    
    if not mt5.connected:
        return jsonify({'error': 'Not connected to MT5'}), 400
    
    try:
        # Get historical data
        df = mt5.get_historical_data(symbol, timeframe, bars=500)
        
        if df is None:
            return jsonify({'error': 'Failed to get data'}), 400
        
        # Calculate indicators
        indicator_engine = IndicatorEngine(df)
        df_indicators = indicator_engine.calculate_all()
        
        # Generate signals
        signal_gen = SignalGenerator(df_indicators)
        df_signals = signal_gen.generate_signals()
        
        # Get ML prediction
        ml_signals, ml_confidence = ml_model.predict(df_signals)
        
        # Combine signals
        df_final = signal_gen.combine_with_ml(df_signals, ml_signals, ml_confidence)
        df_final = signal_gen.filter_signals(df_final)
        
        # Get latest signal
        latest = df_final.iloc[-1]
        current_price = mt5.get_current_price(symbol)
        
        signal_data = {
            'symbol': symbol,
            'timeframe': timeframe,
            'signal': int(latest['final_signal']),
            'signal_text': 'BUY' if latest['final_signal'] == 1 else 'SELL' if latest['final_signal'] == -1 else 'NEUTRAL',
            'confidence': float(latest['ml_confidence']),
            'current_price': current_price,
            'indicators': {
                'rsi': float(latest['rsi']),
                'macd': float(latest['macd']),
                'adx': float(latest['adx']),
                'atr': float(latest['atr']),
                'bb_position': 'upper' if latest['close'] > latest['bb_high'] else 'lower' if latest['close'] < latest['bb_low'] else 'middle'
            },
            'timestamp': df_final.index[-1].isoformat()
        }
        
        current_signals[symbol] = signal_data
        
        return jsonify(signal_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/execute-trade', methods=['POST'])
def execute_trade():
    """Execute a trade based on signal."""
    global mt5, risk_manager
    
    data = request.json
    symbol = data.get('symbol')
    signal = data.get('signal')
    
    if not mt5.connected:
        return jsonify({'error': 'Not connected to MT5'}), 400
    
    try:
        # Get current data
        df = mt5.get_historical_data(symbol, 'H1', bars=100)
        indicator_engine = IndicatorEngine(df)
        df_indicators = indicator_engine.calculate_all()
        
        latest = df_indicators.iloc[-1]
        current_price = mt5.get_current_price(symbol)
        entry_price = current_price['ask'] if signal == 1 else current_price['bid']
        
        # Calculate trade parameters
        atr = latest['atr']
        stop_loss = risk_manager.calculate_stop_loss(entry_price, signal, atr)
        take_profit = risk_manager.calculate_take_profit(entry_price, stop_loss, signal)
        
        stop_pips = abs(entry_price - stop_loss) * 10000
        position_size = risk_manager.calculate_position_size(stop_pips)
        
        # Place order
        order_type = 'buy' if signal == 1 else 'sell'
        result = mt5.place_order(
            symbol=symbol,
            order_type=order_type,
            volume=position_size,
            sl=stop_loss,
            tp=take_profit
        )
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Trade executed successfully',
                'order': {
                    'ticket': result.order,
                    'type': order_type,
                    'entry': entry_price,
                    'sl': stop_loss,
                    'tp': take_profit,
                    'volume': position_size
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to execute trade'
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """Run backtest on historical data."""
    global mt5
    
    data = request.json
    symbol = data.get('symbol', 'EURUSD')
    timeframe = data.get('timeframe', 'H1')
    bars = data.get('bars', 2000)
    
    if not mt5.connected:
        return jsonify({'error': 'Not connected to MT5'}), 400
    
    try:
        # Get historical data
        df = mt5.get_historical_data(symbol, timeframe, bars=bars)
        
        # Calculate indicators
        indicator_engine = IndicatorEngine(df)
        df_indicators = indicator_engine.calculate_all()
        
        # Generate signals
        signal_gen = SignalGenerator(df_indicators)
        df_signals = signal_gen.generate_signals()
        
        # Train ML model
        ml_model_temp = TradingModel()
        ml_model_temp.train(df_signals)
        
        # Get predictions
        ml_signals, ml_confidence = ml_model_temp.predict(df_signals)
        
        # Combine signals
        df_final = signal_gen.combine_with_ml(df_signals, ml_signals, ml_confidence)
        df_final = signal_gen.filter_signals(df_final)
        
        # Run backtest
        backtester = Backtester(initial_balance=10000)
        results = backtester.run(df_final)
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/train-model', methods=['POST'])
def train_model():
    """Train ML model on historical data."""
    global mt5, ml_model
    
    data = request.json
    symbol = data.get('symbol', 'EURUSD')
    timeframe = data.get('timeframe', 'H1')
    
    if not mt5.connected:
        return jsonify({'error': 'Not connected to MT5'}), 400
    
    try:
        # Get historical data
        df = mt5.get_historical_data(symbol, timeframe, bars=3000)
        
        # Calculate indicators
        indicator_engine = IndicatorEngine(df)
        df_indicators = indicator_engine.calculate_all()
        
        # Generate signals
        signal_gen = SignalGenerator(df_indicators)
        df_signals = signal_gen.generate_signals()
        
        # Train model
        train_score, test_score = ml_model.train(df_signals)
        ml_model.save('forex_model.pkl')
        
        return jsonify({
            'success': True,
            'train_score': train_score,
            'test_score': test_score,
            'message': 'Model trained successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/start-trading', methods=['POST'])
def start_trading():
    """Start automated trading."""
    global trading_active
    
    trading_active = True
    
    # Start trading thread
    thread = threading.Thread(target=trading_loop)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Automated trading started'
    })


@app.route('/api/stop-trading', methods=['POST'])
def stop_trading():
    """Stop automated trading."""
    global trading_active
    
    trading_active = False
    
    return jsonify({
        'success': True,
        'message': 'Automated trading stopped'
    })


def trading_loop():
    """Main trading loop for automated trading."""
    global trading_active, mt5, ml_model, current_signals
    
    pairs = config.CURRENCY_PAIRS
    
    while trading_active:
        try:
            for pair in pairs:
                # Analyze pair
                df = mt5.get_historical_data(pair, 'H1', bars=500)
                
                if df is None:
                    continue
                
                # Calculate indicators and signals
                indicator_engine = IndicatorEngine(df)
                df_indicators = indicator_engine.calculate_all()
                
                signal_gen = SignalGenerator(df_indicators)
                df_signals = signal_gen.generate_signals()
                
                ml_signals, ml_confidence = ml_model.predict(df_signals)
                df_final = signal_gen.combine_with_ml(df_signals, ml_signals, ml_confidence)
                df_final = signal_gen.filter_signals(df_final)
                
                latest = df_final.iloc[-1]
                signal = int(latest['final_signal'])
                confidence = float(latest['ml_confidence'])
                
                # Execute trade if signal present
                if signal != 0 and confidence >= config.MIN_CONFIDENCE:
                    current_price = mt5.get_current_price(pair)
                    entry_price = current_price['ask'] if signal == 1 else current_price['bid']
                    
                    atr = latest['atr']
                    stop_loss = risk_manager.calculate_stop_loss(entry_price, signal, atr)
                    take_profit = risk_manager.calculate_take_profit(entry_price, stop_loss, signal)
                    
                    stop_pips = abs(entry_price - stop_loss) * 10000
                    position_size = risk_manager.calculate_position_size(stop_pips)
                    
                    order_type = 'buy' if signal == 1 else 'sell'
                    mt5.place_order(pair, order_type, position_size, sl=stop_loss, tp=take_profit)
            
            # Wait before next iteration
            time.sleep(300)  # Check every 5 minutes
            
        except Exception as e:
            print(f"Error in trading loop: {e}")
            time.sleep(60)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI FOREX TRADER - MT5 VERSION")
    print("="*60)
    
    # Try to load existing model
    try:
        ml_model.load('forex_model.pkl')
        print("✓ Loaded existing ML model")
    except:
        print("ℹ No existing model found. Train from web interface.")
    
    # Run Flask app
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    print(f"\n🌐 Web interface: http://localhost:{port}")
    print(f"📱 From network: http://192.168.100.143:{port}")
    print("\n" + "="*60 + "\n")
    
    # Run without debug mode for faster startup
    app.run(host=host, port=port, debug=False, use_reloader=False)
