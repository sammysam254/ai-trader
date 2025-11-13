"""Advanced Flask app with scalping AI, auto-trading, and real-time logs."""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import threading
import time
import numpy as np

from mt5_connector import MT5Connector
from data_loader import DataLoader
from indicators import IndicatorEngine
from scalping_strategy import ScalpingStrategy
from advanced_ml_model import AdvancedTradingModel
from pattern_recognition import PatternRecognizer
from risk_manager import RiskManager
from trading_logger import trading_logger
from position_manager import PositionManager
import config

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'advanced-trading-key')
CORS(app)

# Global variables
mt5 = MT5Connector()
data_loader = DataLoader()
scalping_strategy = ScalpingStrategy()
ml_model = AdvancedTradingModel()
pattern_recognizer = PatternRecognizer()
risk_manager = None
position_manager = None
trading_active = False
auto_trading_thread = None
account_info = {}


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index_advanced.html')


@app.route('/api/connect', methods=['POST'])
def connect_mt5():
    """Connect to MT5 with provided credentials."""
    global mt5, risk_manager, account_info
    
    try:
        data = request.json
        login = data.get('login')
        password = data.get('password')
        server = data.get('server')
        path = data.get('path', 'C:\\Program Files\\MetaTrader 5\\terminal64.exe')
        
        if not login or not password or not server:
            return jsonify({
                'success': False,
                'message': 'Missing required credentials'
            }), 400
        
        mt5.login = login
        mt5.password = password
        mt5.server = server
        mt5.path = path
        
        trading_logger.info(f"Attempting connection to {server}...")
        
        if mt5.connect():
            account_info = mt5.get_account_info()
            
            if not account_info:
                trading_logger.error("Connected but failed to get account info")
                return jsonify({
                    'success': False,
                    'message': 'Connected but failed to get account info'
                }), 400
            
            risk_manager = RiskManager(account_info['balance'])
            account_type = detect_account_type(server, account_info)
            
            # Initialize position manager
            global position_manager
            position_manager = PositionManager(mt5, scalping_strategy, ml_model, data_loader)
            position_manager.start_monitoring()
            
            trading_logger.success(f"Connected to {account_type} account successfully!")
            trading_logger.info(f"Balance: ${account_info['balance']:.2f}")
            trading_logger.info("Intelligent position monitoring activated")
            
            return jsonify({
                'success': True,
                'message': f'Connected to MT5 ({account_type} account)',
                'account': account_info,
                'account_type': account_type
            })
        else:
            trading_logger.error("Failed to connect to MT5")
            return jsonify({
                'success': False,
                'message': 'Failed to connect. Check credentials and ensure MT5 is installed.'
            }), 400
            
    except Exception as e:
        trading_logger.error(f"Connection error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def detect_account_type(server, account_info):
    """Detect if account is Demo or Real."""
    server_lower = server.lower()
    demo_keywords = ['demo', 'test', 'practice', 'trial', 'contest']
    
    if any(keyword in server_lower for keyword in demo_keywords):
        return 'DEMO'
    
    if account_info:
        name = account_info.get('name', '').lower()
        company = account_info.get('company', '').lower()
        
        if any(keyword in name for keyword in demo_keywords):
            return 'DEMO'
        if any(keyword in company for keyword in demo_keywords):
            return 'DEMO'
    
    return 'REAL'


@app.route('/api/disconnect', methods=['POST'])
def disconnect_mt5():
    """Disconnect from MT5."""
    global mt5, trading_active, position_manager
    
    trading_active = False
    
    # Stop position monitoring
    if position_manager:
        position_manager.stop_monitoring()
    
    mt5.disconnect()
    trading_logger.info("Disconnected from MT5")
    
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
    """Get open positions with real-time P&L."""
    global mt5
    
    if not mt5.connected:
        return jsonify([])
    
    try:
        positions = mt5.get_open_positions()
        return jsonify(positions)
    except Exception as e:
        trading_logger.error(f"Error getting positions: {str(e)}")
        return jsonify([])


@app.route('/api/execute-trade', methods=['POST'])
def execute_trade():
    """Execute a manual trade with custom stake."""
    global mt5, risk_manager
    
    data = request.json
    symbol = data.get('symbol')
    signal = data.get('signal')
    stake_usd = data.get('stake', 10)  # Default $10 stake
    
    if not symbol or not signal:
        return jsonify({
            'success': False,
            'message': 'Missing symbol or signal'
        }), 400
    
    try:
        trading_logger.info(f"Executing manual trade: {symbol} {'BUY' if signal == 1 else 'SELL'} with ${stake_usd} stake")
        
        # Get current data
        if mt5.connected:
            df = mt5.get_historical_data(symbol, 'M5', bars=100)
        else:
            df = data_loader.generate_sample_data(periods=100, pair=symbol)
        
        if df is None:
            return jsonify({
                'success': False,
                'message': 'Failed to get market data'
            }), 400
        
        # Calculate indicators
        indicator_engine = IndicatorEngine(df)
        df_indicators = indicator_engine.calculate_all()
        
        latest = df_indicators.iloc[-1]
        close_price = latest['close']
        atr = latest['atr']
        
        # Get scores for target calculation
        signals, buy_score, sell_score = scalping_strategy.analyze_scalping_opportunity(df_indicators)
        
        # Use proper entry price based on signal direction
        # BUY at ASK (higher), SELL at BID (lower)
        spread = close_price * 0.0002  # Approximate 2 pip spread
        if signal == 1:  # BUY
            entry_price = close_price + spread  # Buy at ASK
        else:  # SELL
            entry_price = close_price - spread  # Sell at BID
        
        # Calculate targets using the correct entry price
        stop_loss, take_profit = scalping_strategy.calculate_scalping_targets(
            entry_price, signal, atr, buy_score.iloc[-1], sell_score.iloc[-1]
        )
        
        # Calculate position size based on stake
        stop_pips = abs(entry_price - stop_loss) * 10000
        position_size = stake_usd / (stop_pips * 10)
        position_size = max(0.01, min(position_size, 2.0))  # Between 0.01 and 2.0 lots
        
        # Execute trade
        print(f"\n{'='*60}")
        print(f"TRADE EXECUTION ATTEMPT")
        print(f"{'='*60}")
        print(f"MT5 Connected: {mt5.connected}")
        print(f"Symbol: {symbol}")
        print(f"Signal: {'BUY' if signal == 1 else 'SELL'}")
        print(f"Position Size: {position_size} lots")
        print(f"Close Price: {close_price:.5f}")
        print(f"Entry Price: {entry_price:.5f} ({'ASK' if signal == 1 else 'BID'})")
        print(f"Stop Loss: {stop_loss:.5f}")
        print(f"Take Profit: {take_profit:.5f}")
        print(f"Risk/Reward: 1:{abs(take_profit - entry_price) / abs(entry_price - stop_loss):.2f}")
        print(f"{'='*60}\n")
        
        if mt5.connected:
            trading_logger.info(f"Placing order via MT5...")
            
            result = mt5.place_order(
                symbol=symbol,
                order_type='buy' if signal == 1 else 'sell',
                volume=position_size,
                sl=stop_loss,
                tp=take_profit,
                comment=f"Manual ${stake_usd}"
            )
            
            print(f"Order result: {result}")
            
            if result:
                trading_logger.success(f"Trade executed successfully: {symbol}")
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
                trading_logger.error("Trade execution failed - MT5 returned None")
                print("ERROR: MT5 place_order returned None")
                return jsonify({
                    'success': False,
                    'message': 'Trade execution failed. Possible reasons:\n1. Insufficient margin\n2. Symbol not found\n3. Invalid volume\n4. Market closed\n5. Check terminal for errors'
                }), 400
        else:
            # Demo mode
            trading_logger.info(f"DEMO: Would execute {symbol} {'BUY' if signal == 1 else 'SELL'} with {position_size} lots at {entry_price:.5f}")
            return jsonify({
                'success': True,
                'message': 'Demo trade simulated (MT5 not connected)',
                'order': {
                    'symbol': symbol,
                    'type': 'buy' if signal == 1 else 'sell',
                    'volume': position_size,
                    'entry': entry_price,
                    'sl': stop_loss,
                    'tp': take_profit
                }
            })
            
    except Exception as e:
        trading_logger.error(f"Trade execution error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/close-position/<int:ticket>', methods=['POST'])
def close_position(ticket):
    """Close a specific position."""
    global mt5
    
    print(f"\n{'='*60}")
    print(f"CLOSE POSITION REQUEST")
    print(f"{'='*60}")
    print(f"Ticket: {ticket}")
    print(f"MT5 Connected: {mt5.connected}")
    print(f"{'='*60}\n")
    
    if not mt5.connected:
        trading_logger.error("Cannot close position - MT5 not connected")
        return jsonify({
            'success': False,
            'message': 'MT5 not connected'
        }), 400
    
    try:
        trading_logger.info(f"Attempting to close position {ticket}...")
        result = mt5.close_position(ticket)
        
        if result:
            trading_logger.success(f"Position {ticket} closed successfully")
            return jsonify({
                'success': True,
                'message': f'Position {ticket} closed successfully'
            })
        else:
            trading_logger.error(f"Failed to close position {ticket}")
            return jsonify({
                'success': False,
                'message': 'Failed to close position. Check:\n1. Position exists\n2. Market is open\n3. No connection issues\n4. Check MT5 terminal for errors'
            }), 400
            
    except Exception as e:
        trading_logger.error(f"Error closing position {ticket}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_pair():
    """Analyze pair with advanced AI."""
    global mt5, ml_model, scalping_strategy, pattern_recognizer
    
    data = request.json
    symbol = data.get('symbol', 'EURUSD')
    timeframe = data.get('timeframe', 'M5')  # Scalping uses lower timeframes
    
    if not mt5.connected:
        # Use demo data
        trading_logger.warning("Using demo data (MT5 not connected)")
        df = data_loader.generate_sample_data(periods=500, pair=symbol)
    else:
        trading_logger.info(f"Analyzing {symbol} on {timeframe}...")
        df = mt5.get_historical_data(symbol, timeframe, bars=500)
        
        if df is None:
            trading_logger.error(f"Failed to get data for {symbol}")
            return jsonify({'error': 'Failed to get data'}), 400
    
    try:
        # Calculate indicators
        trading_logger.info("Calculating 30+ technical indicators...")
        indicator_engine = IndicatorEngine(df)
        df_indicators = indicator_engine.calculate_all()
        
        # Analyze patterns
        trading_logger.info("Analyzing chart patterns...")
        patterns = pattern_recognizer.analyze_patterns(df_indicators)
        bullish_score, bearish_score = pattern_recognizer.get_pattern_score(patterns)
        
        # Generate scalping signals
        trading_logger.info("Generating scalping signals...")
        signals, buy_score, sell_score = scalping_strategy.analyze_scalping_opportunity(df_indicators)
        df_indicators['signal'] = signals
        
        # Apply filters
        trading_logger.info("Applying strict filters...")
        df_indicators['signal'] = scalping_strategy.filter_scalping_signals(df_indicators, df_indicators['signal'])
        
        # Get ML prediction
        trading_logger.info("Running AI prediction model...")
        try:
            ml_signals, ml_confidence = ml_model.predict(df_indicators)
            df_indicators['ml_signal'] = 0
            df_indicators['ml_confidence'] = 0.0
            df_indicators.loc[df_indicators.index[-len(ml_signals):], 'ml_signal'] = ml_signals
            df_indicators.loc[df_indicators.index[-len(ml_confidence):], 'ml_confidence'] = ml_confidence.astype(float)
        except:
            trading_logger.warning("ML model not trained, training now...")
            ml_model.train(df_indicators)
            ml_signals, ml_confidence = ml_model.predict(df_indicators)
            df_indicators['ml_signal'] = 0
            df_indicators['ml_confidence'] = 0.0
            df_indicators.loc[df_indicators.index[-len(ml_signals):], 'ml_signal'] = ml_signals
            df_indicators.loc[df_indicators.index[-len(ml_confidence):], 'ml_confidence'] = ml_confidence.astype(float)
        
        # Combine signals - Only trade when both agree OR ML is very confident
        df_indicators['final_signal'] = np.where(
            (df_indicators['signal'] == df_indicators['ml_signal']) & (df_indicators['signal'] != 0),
            df_indicators['signal'],  # Both agree on direction
            np.where(
                (df_indicators['ml_confidence'] > 0.75) & (df_indicators['ml_signal'] != 0),
                df_indicators['ml_signal'],  # ML is very confident
                0  # No clear signal
            )
        )
        
        # Get latest data
        latest = df_indicators.iloc[-1]
        current_price = latest['close']
        
        # Determine signal
        confidence_pct = latest['ml_confidence'] * 100
        
        if latest['final_signal'] == 1:
            if confidence_pct > 75:
                signal_text = 'STRONG BUY'
                trading_logger.success(f"STRONG BUY signal! Confidence: {confidence_pct:.1f}%")
            else:
                signal_text = 'BUY'
                trading_logger.info(f"BUY signal. Confidence: {confidence_pct:.1f}%")
        elif latest['final_signal'] == -1:
            if confidence_pct > 75:
                signal_text = 'STRONG SELL'
                trading_logger.success(f"STRONG SELL signal! Confidence: {confidence_pct:.1f}%")
            else:
                signal_text = 'SELL'
                trading_logger.info(f"SELL signal. Confidence: {confidence_pct:.1f}%")
        else:
            signal_text = 'NO SIGNAL'
            trading_logger.warning("No clear trading opportunity - waiting for better setup")
        
        signal_data = {
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
                'bid': float(current_price),
                'ask': float(current_price * 1.0001),
                'time': df_indicators.index[-1].isoformat()
            },
            'indicators': {
                'rsi': float(latest['rsi']),
                'macd': float(latest['macd']),
                'adx': float(latest['adx']),
                'atr': float(latest['atr']),
                'ema_12': float(latest['ema_12']),
                'ema_26': float(latest['ema_26'])
            },
            'timestamp': df_indicators.index[-1].isoformat()
        }
        
        return jsonify(signal_data)
        
    except Exception as e:
        trading_logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/logs')
def get_logs():
    """Get recent trading logs."""
    logs = trading_logger.get_logs(100)
    return jsonify(logs)


@app.route('/api/train-model', methods=['POST'])
def train_model():
    """Train the advanced AI model."""
    global ml_model
    
    data = request.json
    symbol = data.get('symbol', 'EURUSD')
    
    try:
        trading_logger.info("🎓 Starting AI model training...")
        trading_logger.info(f"Fetching 3000+ historical bars for {symbol}...")
        
        # Get historical data
        if mt5.connected:
            df = mt5.get_historical_data(symbol, 'M5', bars=3000)
        else:
            df = data_loader.generate_sample_data(periods=3000, pair=symbol)
        
        if df is None or len(df) < 500:
            trading_logger.error("Not enough data for training")
            return jsonify({
                'success': False,
                'error': 'Not enough data for training'
            }), 400
        
        trading_logger.info("Calculating indicators...")
        indicator_engine = IndicatorEngine(df)
        df_indicators = indicator_engine.calculate_all()
        
        trading_logger.info("Generating training signals...")
        signals, _, _ = scalping_strategy.analyze_scalping_opportunity(df_indicators)
        df_indicators['signal'] = signals
        
        trading_logger.info("Training ensemble AI model (this may take 2-3 minutes)...")
        train_score, test_score = ml_model.train(df_indicators)
        
        trading_logger.success(f"✓ Training complete! Train: {train_score*100:.1f}% | Test: {test_score*100:.1f}%")
        
        # Save model
        ml_model.save('advanced_model.pkl')
        trading_logger.success("✓ Model saved successfully")
        
        return jsonify({
            'success': True,
            'train_score': train_score,
            'test_score': test_score,
            'message': 'Model trained successfully'
        })
        
    except Exception as e:
        trading_logger.error(f"Training error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/start-auto-trading', methods=['POST'])
def start_auto_trading():
    """Start automated trading."""
    global trading_active, auto_trading_thread
    
    if trading_active:
        return jsonify({
            'success': False,
            'message': 'Auto trading already running'
        })
    
    trading_active = True
    trading_logger.success("🤖 AUTO TRADING STARTED")
    trading_logger.info("AI will now analyze markets and execute trades automatically")
    
    # Start trading thread
    auto_trading_thread = threading.Thread(target=auto_trading_loop, daemon=True)
    auto_trading_thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Auto trading started'
    })


@app.route('/api/stop-auto-trading', methods=['POST'])
def stop_auto_trading():
    """Stop automated trading."""
    global trading_active
    
    trading_active = False
    trading_logger.warning("🛑 AUTO TRADING STOPPED")
    
    return jsonify({
        'success': True,
        'message': 'Auto trading stopped'
    })


def auto_trading_loop():
    """Main auto-trading loop with real trade execution."""
    global trading_active, mt5, ml_model, scalping_strategy, risk_manager
    
    # Get all available pairs from MT5 or use defaults
    if mt5.connected:
        try:
            import metatrader5 as mt5_lib
            symbols = mt5_lib.symbols_get()
            if symbols:
                # Get USD pairs and GOLD
                pairs = [s.name for s in symbols if 'USD' in s.name or s.name == 'XAUUSD'][:12]
            else:
                pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'XAUUSD']
        except:
            pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'XAUUSD']
    else:
        pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'XAUUSD']
    
    check_interval = 60  # Check every 60 seconds
    fixed_stake_usd = 10  # Fixed $10 stake for auto-trading
    
    trading_logger.info(f"Auto-trading started with ${fixed_stake_usd} stake per trade")
    trading_logger.info(f"Monitoring {len(pairs)} pairs: {', '.join(pairs)}")
    
    while trading_active:
        try:
            for pair in pairs:
                if not trading_active:
                    break
                
                trading_logger.info(f"Scanning {pair}...")
                
                # Get data
                if mt5.connected:
                    df = mt5.get_historical_data(pair, 'M5', bars=500)
                else:
                    df = data_loader.generate_sample_data(periods=500, pair=pair)
                
                if df is None:
                    continue
                
                # Analyze
                indicator_engine = IndicatorEngine(df)
                df_indicators = indicator_engine.calculate_all()
                
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
                    continue
                
                # Combine signals - only trade when confident
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
                signal = int(latest['final_signal'])
                confidence = float(latest['ml_confidence'])
                
                # Skip if no clear signal
                if signal == 0:
                    trading_logger.info(f"{pair}: No clear signal (Confidence: {confidence*100:.1f}%)")
                    continue
                
                # Only trade with high confidence (70%+)
                if confidence < 0.70:
                    trading_logger.info(f"{pair}: Confidence too low ({confidence*100:.1f}%) - skipping")
                    continue
                
                signal_type = "BUY" if signal == 1 else "SELL"
                
                trading_logger.success(f"OPPORTUNITY: {signal_type} {pair} (Confidence: {confidence*100:.1f}%)")
                
                # Execute trade with proper entry price
                close_price = latest['close']
                atr = latest['atr']
                
                # Use proper entry price (BUY at ASK, SELL at BID)
                spread = close_price * 0.0002
                if signal == 1:
                    entry_price = close_price + spread
                else:
                    entry_price = close_price - spread
                
                # Calculate targets
                stop_loss, take_profit = scalping_strategy.calculate_scalping_targets(
                    entry_price, signal, atr, buy_score.iloc[-1], sell_score.iloc[-1]
                )
                
                # Calculate position size based on fixed stake
                stop_pips = abs(entry_price - stop_loss) * 10000
                position_size = fixed_stake_usd / (stop_pips * 10)
                position_size = max(0.01, min(position_size, 1.0))  # Between 0.01 and 1.0 lots
                
                # Execute the trade
                if mt5.connected:
                    try:
                        result = mt5.place_order(
                            symbol=pair,
                            order_type='buy' if signal == 1 else 'sell',
                            volume=position_size,
                            sl=stop_loss,
                            tp=take_profit,
                            comment=f"AI {confidence*100:.0f}%"
                        )
                        if result:
                            trading_logger.success(f"✓ EXECUTED: {signal_type} {pair} @ {entry_price:.5f} | Size: {position_size} | SL: {stop_loss:.5f} | TP: {take_profit:.5f}")
                        else:
                            trading_logger.error(f"Trade execution failed for {pair}")
                    except Exception as e:
                        trading_logger.error(f"Execution error: {str(e)}")
                else:
                    # Demo mode - simulate trade
                    trading_logger.info(f"DEMO: {signal_type} {pair} @ {entry_price:.5f} | Size: {position_size} lots")
                
                time.sleep(2)  # Brief pause between trades
            
            # Wait before next scan
            trading_logger.info(f"Waiting {check_interval}s before next scan...")
            time.sleep(check_interval)
            
        except Exception as e:
            trading_logger.error(f"Auto-trading error: {str(e)}")
            time.sleep(60)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("ADVANCED AI FOREX SCALPING SYSTEM")
    print("="*70)
    
    # Try to load model
    try:
        ml_model.load('advanced_model.pkl')
        print("Advanced AI model loaded")
    except:
        print("No model found. Will train on first use.")
    
    print(f"\n🌐 Web interface: http://localhost:5000")
    print(f"📱 From network: http://192.168.100.143:5000")
    print("\n" + "="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
