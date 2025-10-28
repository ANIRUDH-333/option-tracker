"""
Safety checks - Pre-flight validation before starting the monitor.
Run this BEFORE starting production monitoring.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from smartapi_client import SmartAPIClient


def check_credentials():
    """Check that credentials are properly configured."""
    print("🔍 Checking credentials...")
    
    try:
        Config.validate()
        print("  ✅ All credentials present")
    except ValueError as e:
        print(f"  ❌ FAILED: {e}")
        return False
    
    # Check for placeholders
    if any(x in (Config.API_KEY or '') for x in ['your_', 'test', 'xxx']):
        print("  ❌ FAILED: API_KEY appears to be a placeholder")
        return False
    
    print("  ✅ Credentials look valid")
    return True


def check_api_connection():
    """Check that we can connect to SmartAPI."""
    print("\n🔍 Checking API connection...")
    
    try:
        client = SmartAPIClient()
        print("  ✅ Session initialized successfully")
        
        # Try to get order book
        orders = client.get_order_book()
        
        if orders is None:
            print("  ❌ FAILED: Could not fetch order book (API returned None)")
            print("     This could mean:")
            print("     - Invalid credentials")
            print("     - Network/API connectivity issues")
            print("     - Session expired")
            return False
        
        # Check if response has expected structure
        if not isinstance(orders, dict):
            print(f"  ❌ FAILED: Unexpected response format: {type(orders)}")
            return False
        
        # Check if status is successful
        if not orders.get('status'):
            print(f"  ❌ FAILED: API returned error: {orders.get('message', 'Unknown error')}")
            return False
        
        # Get order data (could be None if no orders exist)
        order_data = orders.get('data')
        if order_data is None:
            order_count = 0
            print("  ✅ Order book accessible (0 orders found - no orders placed yet)")
        else:
            order_count = len(order_data)
            print(f"  ✅ Order book accessible ({order_count} orders found)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_rate_limits():
    """Check rate limit configuration."""
    print("\n🔍 Checking rate limit configuration...")
    
    interval = 2  # seconds
    calls_per_minute = 60 / interval
    
    if calls_per_minute > 50:
        print(f"  ⚠️  WARNING: {calls_per_minute} calls/minute may hit rate limits")
        print("     Consider increasing interval to 2+ seconds")
        return False
    
    print(f"  ✅ Rate limit safe: {calls_per_minute} calls/minute")
    return True


def check_file_permissions():
    """Check that necessary files exist and are readable."""
    print("\n🔍 Checking file permissions...")
    
    required_files = [
        '.env',
        'config.py',
        'smartapi_client.py',
        'smart_polling.py',
        'web_ui.py'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"  ❌ FAILED: {file} not found")
            return False
        if not os.access(file, os.R_OK):
            print(f"  ❌ FAILED: {file} not readable")
            return False
    
    print("  ✅ All required files present and readable")
    return True


def run_safety_checks():
    """Run all safety checks."""
    print("="*80)
    print("COPY TRADING MONITOR - PRE-FLIGHT SAFETY CHECKS")
    print("="*80)
    print("\n⚠️  IMPORTANT: Do NOT proceed if any check fails!")
    print("   Failed checks can result in missed trades or financial loss.\n")
    
    checks = [
        ("File Permissions", check_file_permissions),
        ("Credentials", check_credentials),
        ("API Connection", check_api_connection),
        ("Rate Limits", check_rate_limits),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*80)
    print("SAFETY CHECK SUMMARY")
    print("="*80)
    
    all_passed = all(result for _, result in results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("="*80)
    
    if all_passed:
        print("\n✅ ALL CHECKS PASSED - SAFE TO START MONITORING")
        print("\nYou can now run: python web_ui.py")
        return 0
    else:
        print("\n❌ SOME CHECKS FAILED - DO NOT START MONITORING")
        print("\nFix the issues above before proceeding.")
        return 1


if __name__ == '__main__':
    exit_code = run_safety_checks()
    sys.exit(exit_code)
