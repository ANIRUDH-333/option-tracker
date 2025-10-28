"""
Test script to verify copy trading detection works.
Run this and then place an order in your Angel One app to see it detected.
"""
from smartapi_client import SmartAPIClient
from polling_monitor import PollingOrderMonitor


def main():
    print("="*100)
    print("COPY TRADING TEST - ORDER DETECTION")
    print("="*100)
    print("\n📋 Instructions:")
    print("1. This script will monitor your account for new orders")
    print("2. Open Angel One app/web and place a test order")
    print("3. You should see the order appear here within 3 seconds")
    print("4. Press Ctrl+C to stop monitoring\n")
    print("="*100 + "\n")
    
    # Initialize client
    print("Connecting to SmartAPI...")
    client = SmartAPIClient()
    
    # Start monitoring
    monitor = PollingOrderMonitor(client, check_interval=3)
    
    print("\n✅ Ready! Place an order in Angel One to test detection.\n")
    
    monitor.start()


if __name__ == "__main__":
    main()
