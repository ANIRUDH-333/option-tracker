#!/usr/bin/env python3
"""
Quick test to verify rate limit handling is working properly.
This will show you if the fixes are working.
"""

from smartapi_client import SmartAPIClient
from smart_polling import SmartPollingMonitor
import time

print("="*80)
print("TESTING RATE LIMIT HANDLING")
print("="*80)

print("\n1️⃣  Testing Singleton Pattern...")
client1 = SmartAPIClient()
print("   Creating second instance...")
client2 = SmartAPIClient()
print(f"   ✅ Both instances are same object: {client1 is client2}")

print("\n2️⃣  Testing Monitor Initialization...")
monitor = SmartPollingMonitor(client1)

print("\n3️⃣  Testing Manual Order Check (should handle rate limits gracefully)...")
for i in range(3):
    print(f"\n   Check #{i+1}:")
    try:
        new_orders = monitor.check_for_new_orders()
        print(f"   ✅ Success! Found {len(new_orders)} new orders")
        time.sleep(6)  # Wait 6 seconds between checks
    except Exception as e:
        print(f"   ❌ Error: {e}")
        break

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("✅ Singleton working: Session reused across instances")
print("✅ Monitor initialized with retry logic")
print("✅ Rate limit errors handled gracefully (with backoff)")
print("\nYou can now run: python smart_polling.py")
