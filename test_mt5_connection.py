"""Test MT5 connection with your credentials."""

import os
from dotenv import load_dotenv

print("="*60)
print("Testing MT5 Connection")
print("="*60)

# Load environment variables
load_dotenv()

print("\n[1/4] Loading credentials from .env...")
login = os.getenv('MT5_LOGIN')
server = os.getenv('MT5_SERVER')
path = os.getenv('MT5_PATH')

print(f"  Login: {login}")
print(f"  Server: {server}")
print(f"  Path: {path}")

if login == 'your_mt5_account_number':
    print("\n❌ ERROR: You haven't configured your .env file yet!")
    print("\nPlease edit .env file and add your MT5 credentials.")
    print("See CONFIGURE_MT5.md for instructions.")
    input("\nPress Enter to exit...")
    exit(1)

print("\n[2/4] Importing MetaTrader5...")
try:
    import MetaTrader5 as mt5
    print("  ✓ MetaTrader5 module imported")
except ImportError as e:
    print(f"  ❌ Failed to import MetaTrader5: {e}")
    print("\nMake sure you're using Python 3.11 environment:")
    print("  venv311\\Scripts\\activate.bat")
    input("\nPress Enter to exit...")
    exit(1)

print("\n[3/4] Initializing MT5...")
if not mt5.initialize(path=path):
    error = mt5.last_error()
    print(f"  ❌ Initialization failed: {error}")
    print("\nPossible solutions:")
    print("  1. Check MT5_PATH in .env is correct")
    print("  2. Make sure MetaTrader 5 is installed")
    print("  3. Try running as Administrator")
    mt5.shutdown()
    input("\nPress Enter to exit...")
    exit(1)

print("  ✓ MT5 initialized successfully")

print("\n[4/4] Logging in to account...")
password = os.getenv('MT5_PASSWORD')

authorized = mt5.login(
    login=int(login),
    password=password,
    server=server
)

if not authorized:
    error = mt5.last_error()
    print(f"  ❌ Login failed: {error}")
    print("\nPossible solutions:")
    print("  1. Check MT5_LOGIN is correct (numbers only)")
    print("  2. Verify MT5_PASSWORD is correct")
    print("  3. Confirm MT5_SERVER name matches exactly")
    print("  4. Make sure account is active")
    mt5.shutdown()
    input("\nPress Enter to exit...")
    exit(1)

print("  ✓ Logged in successfully!")

# Get account info
account = mt5.account_info()
if account:
    print("\n" + "="*60)
    print("✓ CONNECTION SUCCESSFUL!")
    print("="*60)
    print(f"\nAccount Information:")
    print(f"  Balance: ${account.balance:.2f}")
    print(f"  Equity: ${account.equity:.2f}")
    print(f"  Margin: ${account.margin:.2f}")
    print(f"  Free Margin: ${account.margin_free:.2f}")
    print(f"  Leverage: 1:{account.leverage}")
    print(f"  Currency: {account.currency}")
    print(f"  Server: {account.server}")
    print(f"  Name: {account.name}")

# Test getting data
print("\n" + "="*60)
print("Testing Data Retrieval")
print("="*60)

print("\nFetching EURUSD data...")
rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_H1, 0, 10)

if rates is not None and len(rates) > 0:
    print(f"  ✓ Retrieved {len(rates)} bars")
    print(f"  Latest close price: {rates[-1]['close']:.5f}")
else:
    print("  ⚠️  Could not get EURUSD data")
    print("  Try a different symbol (check your broker's symbol list)")

# Cleanup
mt5.shutdown()

print("\n" + "="*60)
print("✓ ALL TESTS PASSED!")
print("="*60)
print("\nYou're ready to start trading!")
print("\nRun: start_mt5_version.bat")
print("Then open: http://localhost:5000")

input("\nPress Enter to exit...")
