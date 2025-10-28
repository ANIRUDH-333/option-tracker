"""
Copy trading implementation - mirrors orders from one account to another.
"""
from datetime import datetime
from smartapi_client import SmartAPIClient
from websocket_monitor import OrderMonitor
from config import Config


class CopyTrader:
    """Handles copy trading between two accounts."""
    
    def __init__(self, source_client: SmartAPIClient, target_client: SmartAPIClient = None):
        """
        Initialize copy trader.
        
        Args:
            source_client: SmartAPIClient for the account to monitor
            target_client: SmartAPIClient for the account to copy trades to (optional)
        """
        self.source_client = source_client
        self.target_client = target_client
        self.monitor = OrderMonitor(source_client)
        
        # Override the on_new_order handler to use our copy trading logic
        self.monitor.on_new_order = self.handle_new_order
    
    def handle_new_order(self, order):
        """
        Handle new order detection and mirror it.
        
        Args:
            order: Order dictionary from source account
        """
        print("\n" + "🔔 " * 30)
        print(f"NEW ORDER DETECTED AT {datetime.now()}")
        print("🔔 " * 30 + "\n")
        
        # Display order
        print(f"Source Account Order:")
        print(f"  Symbol: {order.get('tradingsymbol')}")
        print(f"  Type: {order.get('transactiontype')}")
        print(f"  Quantity: {order.get('quantity')}")
        print(f"  Price: {order.get('price')}")
        print(f"  Status: {order.get('status')}")
        print(f"  Order ID: {order.get('orderid')}")
        
        # Only copy completed orders
        if order.get('status') == 'complete':
            if self.target_client:
                self.place_mirror_order(order)
            else:
                print("\n⚠️  Target client not configured. Order not mirrored.")
        else:
            print(f"\n⏳ Order status is '{order.get('status')}', not mirroring yet.")
        
        print("="*100 + "\n")
    
    def place_mirror_order(self, original_order):
        """
        Place a mirror order in the target account.
        
        Args:
            original_order: The original order to copy
        """
        try:
            print(f"\n📤 Placing mirror order in target account...")
            
            # Prepare order parameters
            order_params = {
                'variety': original_order.get('variety', 'NORMAL'),
                'tradingsymbol': original_order.get('tradingsymbol'),
                'symboltoken': original_order.get('symboltoken'),
                'transactiontype': original_order.get('transactiontype'),
                'exchange': original_order.get('exchange'),
                'ordertype': original_order.get('ordertype'),
                'producttype': original_order.get('producttype'),
                'duration': original_order.get('duration', 'DAY'),
                'price': original_order.get('price', '0'),
                'squareoff': '0',
                'stoploss': '0',
                'quantity': original_order.get('quantity'),
            }
            
            # Add trigger price if present
            if original_order.get('triggerprice'):
                order_params['triggerprice'] = original_order.get('triggerprice')
            
            # Place order in target account
            response = self.target_client.client.placeOrder(order_params)
            
            if response and response.get('status'):
                print(f"✅ Mirror order placed successfully!")
                print(f"   Target Order ID: {response.get('data', {}).get('orderid')}")
            else:
                print(f"❌ Failed to place mirror order: {response}")
                
        except Exception as e:
            print(f"❌ Error placing mirror order: {e}")
    
    def start(self, use_websocket=True):
        """
        Start copy trading monitoring.
        
        Args:
            use_websocket: If True, uses WebSocket for real-time updates.
                          If False, uses polling (checks every 3 seconds).
        """
        print("="*100)
        print("COPY TRADING MONITOR STARTED")
        print("="*100)
        print(f"Source Account: {Config.CLIENT_ID}")
        if self.target_client:
            print(f"Target Account: Configured ✅")
        else:
            print(f"Target Account: Not configured ⚠️  (will only display orders)")
        print("="*100 + "\n")
        
        if use_websocket:
            print("Using WebSocket for real-time monitoring...")
            self.monitor.start_monitoring()
        else:
            print("Using polling method (checks every 3 seconds)...")
            self.monitor.start_polling_monitor(interval=3)


def main():
    """Example usage of copy trader."""
    # Initialize source account client
    source_client = SmartAPIClient()
    
    # TODO: Initialize target account client with different credentials
    # Create a separate config for the target account or pass credentials directly
    # target_client = SmartAPIClient()  # You'll need separate credentials
    target_client = None  # Set to None for testing (will only display, not copy)
    
    # Create copy trader
    copy_trader = CopyTrader(source_client, target_client)
    
    # Start monitoring
    # Try WebSocket first, falls back to polling if WebSocket fails
    copy_trader.start(use_websocket=True)


if __name__ == "__main__":
    main()
