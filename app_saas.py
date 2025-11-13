"""Multi-user SaaS Flask app with OANDA integration."""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import threading
import time
import numpy as np
from datetime import datetime, timedelta

from broker_manager import BrokerManager, get_available_brokers, get_broker_details
from data_loader import DataLoader
from indicators import IndicatorEngine
from scalping_strategy import ScalpingStrategy
from advanced_ml_model import AdvancedTradingModel
from pattern_recognition import PatternRecognizer
from trading_logger import trading_logger
import config

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///trading_saas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

db = SQLAlchemy(app)

# Global ML model (shared across users)
ml_model = AdvancedTradingModel()
scalping_strategy = ScalpingStrategy()
pattern_recognizer = PatternRecognizer()
data_loader = DataLoader()

# User trading sessions
user_sessions = {}  # {user_id: {'connector': OandaConnector, 'trading_active': bool}}


# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(db.Model):
    """User account model."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Broker credentials (encrypted in production)
    broker_type = db.Column(db.String(50), default='deriv')  # mt5, deriv, oanda
    broker_credentials = db.Column(db.Text)  # JSON string of credentials
    broker_demo = db.Column(db.Boolean, default=True)
    
    # Subscription
    subscription_plan = db.Column(db.String(50), default='free')  # free, basic, pro
    subscription_status = db.Column(db.String(50), default='active')
    subscription_expires = db.Column(db.DateTime)
    stripe_customer_id = db.Column(db.String(100))
    
    # Relationships
    trades = db.relationship('Trade', backref='user', lazy=True)


class Trade(db.Model):
    """Trade history model."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    symbol = db.Column(db.String(20), nullable=False)
    trade_type = db.Column(db.String(10), nullable=False)  # buy/sell
    volume = db.Column(db.Float, nullable=False)
    
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float)
    
    sl = db.Column(db.Float)
    tp = db.Column(db.Float)
    
    profit = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='open')  # open, closed
    
    opened_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    broker_trade_id = db.Column(db.String(100))


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/')
def index():
    """Landing page."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')


@app.route('/dashboard')
def dashboard():
    """User dashboard."""
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)


@app.route('/api/signup', methods=['POST'])
def signup():
    """User registration."""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password required'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        # Create user
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            subscription_plan='free',
            subscription_expires=datetime.utcnow() + timedelta(days=7)  # 7-day free trial
        )
        
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        
        return jsonify({
            'success': True,
            'message': 'Account created! 7-day free trial activated.',
            'user': {
                'id': user.id,
                'email': user.email,
                'plan': user.subscription_plan
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """User login."""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        session['user_id'] = user.id
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'plan': user.subscription_plan,
                'expires': user.subscription_expires.isoformat() if user.subscription_expires else None
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout."""
    session.pop('user_id', None)
    return jsonify({'success': True})


# ============================================================================
# BROKER CONNECTION ROUTES
# ============================================================================

@app.route('/api/brokers')
def get_brokers():
    """Get list of available brokers."""
    country = request.args.get('country', 'kenya')
    available = get_available_brokers(country)
    details = get_broker_details()
    
    # Add MT5 broker presets
    from mt5_brokers import get_brokers_by_country as get_mt5_brokers
    mt5_brokers = get_mt5_brokers(country)
    
    return jsonify({
        'available': available,
        'details': {k: v for k, v in details.items() if k in available},
        'mt5_brokers': mt5_brokers
    })


@app.route('/api/mt5-brokers')
def get_mt5_broker_list():
    """Get list of MT5 broker presets."""
    from mt5_brokers import MT5_BROKERS, get_brokers_by_country as get_mt5_brokers
    
    country = request.args.get('country', 'kenya')
    available = get_mt5_brokers(country)
    
    # Return only available brokers for the country
    brokers = {k: v for k, v in MT5_BROKERS.items() if k in available or k == 'other'}
    
    return jsonify({
        'brokers': brokers,
        'recommended': available[:3] if available else []
    })


@app.route('/api/connect-broker', methods=['POST'])
def connect_broker():
    """Connect user's broker account (MT5, Deriv, or OANDA)."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        data = request.json
        broker_type = data.get('broker_type', 'deriv')
        credentials = data.get('credentials', {})
        demo = data.get('demo', True)
        
        # Validate credentials based on broker type
        if broker_type == 'mt5':
            required = ['login', 'password', 'server']
        elif broker_type == 'deriv':
            required = ['api_token']
        elif broker_type == 'oanda':
            required = ['api_key', 'account_id']
        else:
            return jsonify({'success': False, 'message': 'Invalid broker type'}), 400
        
        for field in required:
            if field not in credentials:
                return jsonify({'success': False, 'message': f'Missing {field}'}), 400
        
        # Test connection
        broker = BrokerManager(broker_type, demo=demo, **credentials)
        if not broker.connect():
            return jsonify({'success': False, 'message': f'Failed to connect to {broker_type.upper()}'}), 400
        
        # Save credentials (encrypt in production!)
        import json as json_lib
        user.broker_type = broker_type
        user.broker_credentials = json_lib.dumps(credentials)
        user.broker_demo = demo
        db.session.commit()
        
        # Store in session
        user_sessions[user_id] = {
            'broker': broker,
            'trading_active': False
        }
        
        # Get account info
        account_info = broker.get_account_info()
        broker_info = broker.get_broker_info()
        
        return jsonify({
            'success': True,
            'message': f'Connected to {broker_info["name"]} successfully',
            'account': account_info,
            'account_type': 'DEMO' if demo else 'LIVE',
            'broker': broker_info
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/disconnect-broker', methods=['POST'])
def disconnect_broker():
    """Disconnect broker."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    if user_id in user_sessions:
        user_sessions[user_id]['broker'].disconnect()
        del user_sessions[user_id]
    
    return jsonify({'success': True})


@app.route('/api/account')
def get_account():
    """Get account information."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    if user_id not in user_sessions:
        return jsonify({'error': 'Not connected to broker'}), 400
    
    try:
        broker = user_sessions[user_id]['broker']
        account_info = broker.get_account_info()
        
        if account_info:
            return jsonify(account_info)
        else:
            return jsonify({'error': 'Failed to get account info'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# TRADING ROUTES
# ============================================================================

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze a trading pair."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Check subscription
    if user.subscription_plan == 'free':
        # Free users: limited features
        pass
    
    try:
        data = request.json
        symbol = data.get('symbol', 'EURUSD')
        timeframe = data.get('timeframe', 'M5')
        
        # Get broker
        if user_id in user_sessions:
            broker = user_sessions[user_id]['broker']
            df = broker.get_historical_data(symbol, timeframe, bars=500)
        else:
            # Use demo data if not connected
            df = data_loader.generate_sample_data(periods=500, pair=symbol)
        
        if df is None:
            return jsonify({'error': 'Failed to get data'}), 400
        
        # Calculate indicators
        indicator_engine = IndicatorEngine(df)
        df_indicators = indicator_engine.calculate_all()
        
        # Analyze patterns
        patterns = pattern_recognizer.analyze_patterns(df_indicators)
        bullish_score, bearish_score = pattern_recognizer.get_pattern_score(patterns)
        
        # Generate signals
        signals, buy_score, sell_score = scalping_strategy.analyze_scalping_opportunity(df_indicators)
        df_indicators['signal'] = signals
        df_indicators['signal'] = scalping_strategy.filter_scalping_signals(df_indicators, df_indicators['signal'])
        
        # ML prediction
        try:
            ml_signals, ml_confidence = ml_model.predict(df_indicators)
            df_indicators['ml_signal'] = 0
            df_indicators['ml_confidence'] = 0.0
            df_indicators.loc[df_indicators.index[-len(ml_signals):], 'ml_signal'] = ml_signals
            df_indicators.loc[df_indicators.index[-len(ml_confidence):], 'ml_confidence'] = ml_confidence.astype(float)
        except:
            ml_model.train(df_indicators)
            ml_signals, ml_confidence = ml_model.predict(df_indicators)
            df_indicators['ml_signal'] = 0
            df_indicators['ml_confidence'] = 0.0
            df_indicators.loc[df_indicators.index[-len(ml_signals):], 'ml_signal'] = ml_signals
            df_indicators.loc[df_indicators.index[-len(ml_confidence):], 'ml_confidence'] = ml_confidence.astype(float)
        
        # Combine signals
        df_indicators['final_signal'] = np.where(
            (df_indicators['signal'] == df_indicators['ml_signal']) & (df_indicators['signal'] != 0),
            df_indicators['signal'],
            np.where(
                (df_indicators['ml_confidence'] > 0.75) & (df_indicators['ml_signal'] != 0),
                df_indicators['ml_signal'],
                0
            )
        )
        
        latest = df_indicators.iloc[-1]
        confidence_pct = latest['ml_confidence'] * 100
        
        if latest['final_signal'] == 1:
            signal_text = 'STRONG BUY' if confidence_pct > 75 else 'BUY'
        elif latest['final_signal'] == -1:
            signal_text = 'STRONG SELL' if confidence_pct > 75 else 'SELL'
        else:
            signal_text = 'NO SIGNAL'
        
        return jsonify({
            'symbol': symbol,
            'timeframe': timeframe,
            'signal': int(latest['final_signal']),
            'signal_text': signal_text,
            'confidence': float(latest['ml_confidence']),
            'buy_score': float(buy_score.iloc[-1]),
            'sell_score': float(sell_score.iloc[-1]),
            'bullish_patterns': int(bullish_score),
            'bearish_patterns': int(bearish_score),
            'current_price': {
                'bid': float(latest['close']),
                'ask': float(latest['close'] * 1.0001),
                'time': df_indicators.index[-1].isoformat()
            },
            'indicators': {
                'rsi': float(latest['rsi']),
                'macd': float(latest['macd']),
                'adx': float(latest['adx']),
                'atr': float(latest['atr'])
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/execute-trade', methods=['POST'])
def execute_trade():
    """Execute a trade."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Check subscription
    if user.subscription_plan == 'free':
        return jsonify({'error': 'Upgrade to Basic or Pro plan to trade'}), 403
    
    # Check if connected
    if user_id not in user_sessions:
        return jsonify({'error': 'Not connected to broker'}), 400
    
    try:
        data = request.json
        symbol = data.get('symbol')
        signal = data.get('signal')
        stake = data.get('stake', 10)
        
        broker = user_sessions[user_id]['broker']
        
        # Get data and calculate targets
        df = broker.get_historical_data(symbol, 'M5', bars=100)
        indicator_engine = IndicatorEngine(df)
        df_indicators = indicator_engine.calculate_all()
        
        latest = df_indicators.iloc[-1]
        close_price = latest['close']
        atr = latest['atr']
        
        signals, buy_score, sell_score = scalping_strategy.analyze_scalping_opportunity(df_indicators)
        
        spread = close_price * 0.0002
        entry_price = close_price + spread if signal == 1 else close_price - spread
        
        stop_loss, take_profit = scalping_strategy.calculate_scalping_targets(
            entry_price, signal, atr, buy_score.iloc[-1], sell_score.iloc[-1]
        )
        
        stop_pips = abs(entry_price - stop_loss) * 10000
        position_size = stake / (stop_pips * 10)
        position_size = max(0.01, min(position_size, 2.0))
        
        # Execute trade
        result = broker.place_order(
            symbol=symbol,
            order_type='buy' if signal == 1 else 'sell',
            volume=position_size,
            sl=stop_loss,
            tp=take_profit,
            comment=f"AI ${stake}"
        )
        
        if result:
            # Save to database
            trade = Trade(
                user_id=user_id,
                symbol=symbol,
                trade_type='buy' if signal == 1 else 'sell',
                volume=position_size,
                entry_price=entry_price,
                sl=stop_loss,
                tp=take_profit,
                broker_trade_id=str(result.deal)
            )
            db.session.add(trade)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Trade executed successfully',
                'order': {
                    'ticket': result.order,
                    'symbol': symbol,
                    'type': 'buy' if signal == 1 else 'sell',
                    'volume': position_size,
                    'entry': entry_price,
                    'sl': stop_loss,
                    'tp': take_profit
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Trade execution failed'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/positions')
def get_positions():
    """Get open positions."""
    if 'user_id' not in session:
        return jsonify([])
    
    user_id = session['user_id']
    
    if user_id not in user_sessions:
        return jsonify([])
    
    try:
        broker = user_sessions[user_id]['broker']
        positions = broker.get_open_positions()
        return jsonify(positions)
    except:
        return jsonify([])


@app.route('/api/close-position/<ticket>', methods=['POST'])
def close_position(ticket):
    """Close a position."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    if user_id not in user_sessions:
        return jsonify({'error': 'Not connected'}), 400
    
    try:
        broker = user_sessions[user_id]['broker']
        result = broker.close_position(ticket)
        
        if result:
            # Update database
            trade = Trade.query.filter_by(broker_trade_id=ticket, user_id=user_id).first()
            if trade:
                trade.status = 'closed'
                trade.closed_at = datetime.utcnow()
                db.session.commit()
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# SUBSCRIPTION ROUTES (Stripe integration)
# ============================================================================

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    """Subscribe to a plan (Stripe integration needed)."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    # TODO: Integrate Stripe
    # For now, just update the plan
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    data = request.json
    plan = data.get('plan')  # 'basic' or 'pro'
    
    user.subscription_plan = plan
    user.subscription_expires = datetime.utcnow() + timedelta(days=30)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Subscribed to {plan} plan'})


# ============================================================================
# ADMIN ROUTES
# ============================================================================

@app.route('/api/admin/stats')
def admin_stats():
    """Admin statistics."""
    # TODO: Add admin authentication
    
    total_users = User.query.count()
    free_users = User.query.filter_by(subscription_plan='free').count()
    basic_users = User.query.filter_by(subscription_plan='basic').count()
    pro_users = User.query.filter_by(subscription_plan='pro').count()
    
    total_trades = Trade.query.count()
    open_trades = Trade.query.filter_by(status='open').count()
    
    return jsonify({
        'users': {
            'total': total_users,
            'free': free_users,
            'basic': basic_users,
            'pro': pro_users
        },
        'trades': {
            'total': total_trades,
            'open': open_trades
        }
    })


# ============================================================================
# INITIALIZE DATABASE
# ============================================================================

with app.app_context():
    db.create_all()
    print("Database initialized")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("MULTI-USER TRADING SAAS PLATFORM")
    print("="*70)
    print(f"\n🌐 Web interface: http://localhost:5000")
    print("\n" + "="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
