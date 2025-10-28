"""
Test to verify SmartAPIClient singleton behavior.
This should only create ONE session even with multiple instances.
"""
from smartapi_client import SmartAPIClient

print("="*80)
print("TESTING SINGLETON PATTERN")
print("="*80)

print("\n1. Creating first SmartAPIClient instance...")
client1 = SmartAPIClient()

print("\n2. Creating second SmartAPIClient instance...")
client2 = SmartAPIClient()

print("\n3. Creating third SmartAPIClient instance...")
client3 = SmartAPIClient()

print("\n" + "="*80)
print("VERIFICATION")
print("="*80)
print(f"client1 is client2: {client1 is client2}")
print(f"client2 is client3: {client2 is client3}")
print(f"All instances are the same object: {client1 is client2 is client3}")
print(f"Session initialized at: {client1.session_time}")
print("\n✅ If you see 'Reusing existing session' messages above, the singleton is working!")
