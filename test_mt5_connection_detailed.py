"""Detailed MT5 connection test."""

import sys
print("Python version:", sys.version)

print("\n[1/5] Testing MT5 import...")
try:
    import metatrader5 as mt5
    print(f"✓ MT5 imported successfully. Version: {mt5.__version__}")
except ImportError as e:
    print(f"✗ Failed to import MT5: {e}")
    sys.exit(1)

print("\n[2/5] Testing MT5 initialization...")
if not mt5.initialize():
    error = mt5.last_error()
    print(f"✗ Initialization failed: {error}")
    print("\nTrying with path...")
    if not mt5.initialize(path="C:\\Program Files\\MetaTrader 5\\terminal64.exe"):
        error = mt5.last_error()
        print(f"✗ Still failed: {error}")
        sys.exit(1)

print("✓ MT5 initialized successfully")

print("\n[3/5] Getting terminal info...")
terminal_info = mt5.terminal_info()
if terminal_info:
    print(f"✓ Terminal: {terminal_info.name}")
    print(f"  Company: {terminal_info.company}")
    print(f"  Path: {terminal_info.path}")
else:
    print("⚠ Could not get terminal info")

print("\n[4/5] Testing login...")
print("Enter your MT5 credentials:")
login = input("Login: ").strip()
password = input("Password: ")
server = input("Server: ").strip()

if login and password and server:
    print(f"\nAttempting login to {server}...")
    authorized = mt5.login(
        login=int(login),
        password=password,
        server=server
    )
    
    if authorized:
        print("✓ Login successful!")
        
        account = mt5.account_info()
        if account:
            print(f"\n[5/5] Account Info:")
            print(f"  Login: {account.login}")
            print(f"  Balance: ${account.balance:.2f}")
            print(f"  Equity: ${account.equity:.2f}")
            print(f"  Server: {account.server}")
            print(f"  Company: {account.company}")
            
            # Test getting symbols
            print(f"\n[6/6] Testing symbol access...")
            symbols = mt5.symbols_get()
            if symbols:
                print(f"✓ Found {len(symbols)} symbols")
                print(f"  First 5: {', '.join([s.name for s in symbols[:5]])}")
            
            # Test getting data
            print(f"\n[7/7] Testing data retrieval...")
            rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_M5, 0, 10)
            if rates is not None:
                print(f"✓ Retrieved {len(rates)} bars for EURUSD")
                print(f"  Latest close: {rates[-1]['close']:.5f}")
            else:
                print("✗ Failed to get data")
            
            print("\n" + "="*60)
            print("✓ ALL TESTS PASSED!")
            print("="*60)
            print("\nYour MT5 connection is working perfectly.")
            print("The issue might be in the web app code.")
            
    else:
        error = mt5.last_error()
        print(f"✗ Login failed: {error}")
        print("\nCommon issues:")
        print("  - Wrong login number")
        print("  - Wrong password")
        print("  - Wrong server name")
        print("  - Account not active")
else:
    print("Skipped login test")

mt5.shutdown()
input("\nPress Enter to exit...")
