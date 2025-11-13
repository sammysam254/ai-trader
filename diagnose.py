"""Diagnostic script to check system status."""

import sys
import os

print("="*70)
print("AI FOREX TRADER - SYSTEM DIAGNOSTIC")
print("="*70)

# Check Python version
print(f"\n✓ Python Version: {sys.version}")
print(f"  Executable: {sys.executable}")

# Check packages
print("\n" + "="*70)
print("CHECKING REQUIRED PACKAGES")
print("="*70)

packages = {
    'pandas': 'Data manipulation',
    'numpy': 'Numerical computing',
    'sklearn': 'Machine learning',
    'ta': 'Technical analysis',
    'flask': 'Web framework',
    'metatrader5': 'MT5 connection'
}

all_ok = True
for package, description in packages.items():
    try:
        if package == 'sklearn':
            __import__('sklearn')
        else:
            __import__(package)
        print(f"✓ {package:15} - {description}")
    except ImportError:
        print(f"✗ {package:15} - {description} (NOT INSTALLED)")
        all_ok = False

# Check MT5 specifically
print("\n" + "="*70)
print("METATRADER 5 STATUS")
print("="*70)

try:
    import metatrader5 as mt5
    print(f"✓ MetaTrader5 package installed")
    print(f"  Version: {mt5.__version__}")
    
    # Try to initialize
    print("\n  Testing MT5 initialization...")
    if mt5.initialize():
        print("  ✓ MT5 initialized successfully")
        terminal_info = mt5.terminal_info()
        if terminal_info:
            print(f"  ✓ Terminal: {terminal_info.name}")
            print(f"    Company: {terminal_info.company}")
            print(f"    Build: {terminal_info.build}")
        mt5.shutdown()
    else:
        error = mt5.last_error()
        print(f"  ✗ MT5 initialization failed: {error}")
        print("\n  Possible issues:")
        print("    - MetaTrader 5 is not installed")
        print("    - MT5 is installed in non-standard location")
        print("    - MT5 is currently running (close it)")
        all_ok = False
        
except ImportError:
    print("✗ MetaTrader5 package NOT installed")
    print("\n  Install with: pip install MetaTrader5")
    all_ok = False

# Check files
print("\n" + "="*70)
print("CHECKING PROJECT FILES")
print("="*70)

required_files = [
    'app.py',
    'mt5_connector.py',
    'indicators.py',
    'ml_model.py',
    'signal_generator.py',
    'risk_manager.py',
    'templates/index.html',
    'static/script.js',
    'static/style.css'
]

for file in required_files:
    if os.path.exists(file):
        print(f"✓ {file}")
    else:
        print(f"✗ {file} (MISSING)")
        all_ok = False

# Check .env
print("\n" + "="*70)
print("CONFIGURATION")
print("="*70)

if os.path.exists('.env'):
    print("✓ .env file exists")
    with open('.env', 'r') as f:
        content = f.read()
        if 'your_mt5_account_number' in content:
            print("  ⚠ .env file not configured yet")
            print("    Edit .env with your MT5 credentials")
        else:
            print("  ✓ .env appears to be configured")
else:
    print("✗ .env file not found")
    print("  Copy .env.example to .env and configure it")
    all_ok = False

# Final status
print("\n" + "="*70)
if all_ok:
    print("✓ ALL CHECKS PASSED!")
    print("="*70)
    print("\nYou're ready to start trading!")
    print("\nRun: START_TRADING.bat")
    print("Or:  python app.py")
else:
    print("✗ SOME ISSUES FOUND")
    print("="*70)
    print("\nPlease fix the issues above before starting.")

print("\n")
input("Press Enter to exit...")
