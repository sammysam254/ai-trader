"""Flask web application for AI Forex Trader - DEMO MODE (No MT5 required)."""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

from data_loader import DataLoader
from indicators import IndicatorEngine
from signal_generator import SignalGenerator
from ml_model import TradingModel
from risk_manager import RiskManager
from backtester import Backtester
import config

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'demo-secret-key-change-this')
CORS(app)

# Global variables
data_loader = DataLoader()
ml_model = TradingModel()
risk_manager = RiskManager(10000)
demo_account = {
    'balance': 10000.00,
    'equity': 10000.00,
    'margin': 0.00,
    'free_margin': 10000.00,
    'profit': 0.00,
    'currency': 'USD',
    'leverage': 100
}
demo_positions = []


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/api/connect', methods=['POST'])
def connect_demo():
    """Connect to demo mode."""
    return jsonify({
        'success': True,
        'message': 'Connected to DEMO mode (using sample data)',
        'account': demo_account
    })


@app.route('/api/disconnect', methods=['POST'])
def disconnect_demo():
    """Disconnect from demo."""
    return jsonify({
        'success': True,
        'message': 'Disconnected from demo mode'
    })


@app.route('/api/account')
def get_account():
    """Get account information."""
    return jsonify(demo_account)


@app.route('/api/positions')
def get_positions():
    """Get open positions."""
    return jsonify(demo_positions)


@app.route('/api/close-position/<int:ticket>', methods=['POST'])
def close_position(ticket):
    """Close a specific position."""
    global demo_positions, demo_account
    
    position = next((p for p in demo_positions if p['ticket'] == ticket), None)
    
    if not position:
        return jsonify({'error': 'Position not found'}), 404
    
    # Calculate profit
    profit = position['profit']
    demo_account['balance'] += profit
    demo_account['equity'] = demo_account['balance']
    demo_account['profit'] -= profit
    
    # Remove position
    demo_positions = [p for p in demo_positions if p['ticket'] != ticket]
    
    return jsonify({
        'success': True,
        'message': f'Position {ticket} closed with profit: ${profit:.2f}'
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_pair():
    """Analyze a currency pair and generate signals."""
    global ml_model
    
    data = request.json
    symbol = data.get('symbol', 'EURUSD')
    timeframe = data.get('timeframe', 'H1')
    
    try:
        # Generate sample data
        df = data_loader.generate_sample_data(periods=500, pair=symbol)
        
        # Calculate indicators
        indicator_engine = IndicatorEngine(df)
        df_indicators = indicator_engine.calculate_all()
        
        # Generate signals
        signal_gen = SignalGenerator(df_indicators)
        df_signals = signal_gen.generate_signals()
        
        # Get ML prediction (train if not trained)
        try:
            ml_signals, ml_confidence = ml_model.predict(df_signals)
        except:
            # Train model first
            ml_model.train(df_signals)
            ml_signals, ml_confidence = ml_model.predict(df_signals)
        
        # Combine signals
        df_final = signal_gen.combine_with_ml(df_signals, ml_signals, ml_confidence)
        df_final = signal_gen.filter_signals(df_final)
        
        # Get latest signal
        latest = df_final.iloc[-1]
        current_price = latest['close']
        
        signal_data = {
            'symbol': symbol,
            'timeframe': timeframe,
            'signal': int(latest['final_signal']),
            'signal_text': 'BUY' if latest['final_signal'] == 1 else 'SELL' if latest['final_signal'] == -1 else 'NEUTRAL',
            'confidence': float(latest['ml_confidence']) if latest['ml_confidence'] > 0 else 0.5,
            'current_price': {
                'bid': float(current_price),
                'ask': float(current_price * 1.0001),
                'time': df_final.index[-1].isoformat()
            },
            'indicators': {
                'rsi': float(latest['rsi']),
                'macd': float(latest['macd']),
                'adx': float(latest['adx']),
                'atr': float(latest['atr']),
                'bb_position': 'upper' if latest['close'] > latest['bb_high'] else 'lower' if latest['close'] < latest['bb_low'] else 'middle'
            },
            'timestamp': df_final.index[-1].isoformat()
        }
        
        return jsonify(signal_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/execute-trade', methods=['POST'])
def execute_trade():
    """Execute a demo trade."""
    global demo_positions, demo_account
    
    data = request.json
    symbol = data.get('symbol')
    signal = data.get('signal')
    
    try:
        # Generate data for this pair
        df = data_loader.generate_sample_data(periods=100, pair=symbol)
        indicator_engine = IndicatorEngine(df)
        df_indicators = indicator_engine.calculate_all()
        
        latest = df_indicators.iloc[-1]
        current_price = latest['close']
        entry_price = current_price * 1.0001 if signal == 1 else current_price
        
        # Calculate trade parameters
        atr = latest['atr']
        stop_loss = risk_manager.calculate_stop_loss(entry_price, signal, atr)
        take_profit = risk_manager.calculate_take_profit(entry_price, stop_loss, signal)
        
        stop_pips = abs(entry_price - stop_loss) * 10000
        position_size = risk_manager.calculate_position_size(stop_pips)
        
        # Create position
        ticket = len(demo_positions) + 1000
        position = {
            'ticket': ticket,
            'symbol': symbol,
            'type': 'buy' if signal == 1 else 'sell',
            'volume': position_size,
            'price_open': entry_price,
            'price_current': entry_price,
            'sl': stop_loss,
            'tp': take_profit,
            'profit': 0.00,
            'time': df_indicators.index[-1].isoformat()
        }
        
        demo_positions.append(position)
        
        return jsonify({
            'success': True,
            'message': 'Demo trade executed successfully',
            'order': {
                'ticket': ticket,
                'type': 'buy' if signal == 1 else 'sell',
                'entry': entry_price,
                'sl': stop_loss,
                'tp': take_profit,
                'volume': position_size
            }
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """Run backtest on historical data."""
    data = request.json
    symbol = data.get('symbol', 'EURUSD')
    timeframe = data.get('timeframe', 'H1')
    bars = data.get('bars', 2000)
    
    try:
        # Generate sample data
        df = data_loader.generate_sample_data(periods=bars, pair=symbol)
        
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
    """Train ML model on sample data."""
    global ml_model
    
    data = request.json
    symbol = data.get('symbol', 'EURUSD')
    
    try:
        # Generate sample data
        df = data_loader.generate_sample_data(periods=3000, pair=symbol)
        
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
            'message': 'Model trained successfully on sample data'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI FOREX TRADER - DEMO MODE")
    print("="*60)
    print("\n⚠️  Running in DEMO mode with sample data")
    print("   To use real MT5 data, install Python 3.11 and MetaTrader5")
    print("   See PYTHON_VERSION_FIX.md for instructions\n")
    print("🌐 Web interface: http://localhost:5000")
    print("📱 From phone/tablet: http://YOUR_IP:5000\n")
    print("="*60 + "\n")
    
    # Try to load existing model
    try:
        ml_model.load('forex_model.pkl')
        print("✓ Loaded existing ML model\n")
    except:
        print("ℹ️  No existing model found. Train a new model from the web interface.\n")
    
    # Run Flask app
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    app.run(host=host, port=port, debug=False)
