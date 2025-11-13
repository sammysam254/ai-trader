"""Quick MT5 connection test."""

print("="*60)
print("Quick MT5 Connection Test")
print("="*60)

# Test 1: Import
print("\n[1/4] Testing import...")
try:
    import metatrader5 as mt5
    print("✓ MetaTrader5 imported successfully")
    print(f"  Version: {mt5.__version__}")
except ImportError as e:
    print(f"✗ Failed to import: {e}")
    exit(1)

# Test 2: Initialize
print("\n[2/4] Testing initialization...")
if not mt5.initialize():
    print(f"✗ Initialization failed: {mt5.last_error()}")
    print("\nTrying with default path...")
    if not mt5.initialize(path="C:\\Program Files\\MetaTrader 5\\terminal64.exe"):
        print(f"✗ Still failed: {mt5.last_error()}")
        print("\nPossible issues:")
        print("  - MetaTrader 5 is not installed")
        print("  - MT5 is installed in a different location")
        print("  - MT5 is not closed (close it and try again)")
        exit(1)

print("✓ MT5 initialized successfully")

# Test 3: Get terminal info
print("\n[3/4] Getting terminal info...")
terminal_info = mt5.terminal_info()
if terminal_info:
    print(f"✓ Terminal: {terminal_info.name}")
    print(f"  Company: {terminal_info.company}")
    print(f"  Path: {terminal_info.path}")
    print(f"  Build: {terminal_info.build}")
else:
    print("⚠ Could not get terminal info")

# Test 4: Test login (you need to provide credentials)
print("\n[4/4] Testing login...")
print("\nTo test login, enter your credentials:")
print("(Press Enter to skip)")

login = input("Login: ").strip()
if login:
    password = input("Password: ")
    server = input("Server: ").strip()
    
    if login and password and server:
        authorized = mt5.login(
            login=int(login),
            password=password,
            server=server
        )
        
        if authorized:
            print("✓ Login successful!")
            account = mt5.account_info()
            if account:
                print(f"  Account: {account.login}")
                print(f"  Balance: ${account.balance:.2f}")
                print(f"  Server: {account.server}")
        else:
            error = mt5.last_error()
            print(f"✗ Login failed: {error}")
            print("\nCommon issues:")
            print("  - Wrong login number")
            print("  - Wrong password")
            print("  - Wrong server name (check exact spelling)")
            print("  - Account is not active")
    else:
        print("Skipped login test")
else:
    print("Skipped login test")

# Cleanup
mt5.shutdown()

print("\n" + "="*60)
print("Test Complete!")
print("="*60)
print("\nIf initialization worked, MT5 is properly installed.")
print("If login failed, check your credentials in MT5:")
print("  Tools → Options → Server tab")
