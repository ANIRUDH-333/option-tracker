"""
Simple polling-based order monitor (more reliable than WebSocket).
Checks for new orders every few seconds.
"""
import time
from datetime import datetime
from smartapi_client import SmartAPIClient
from display import display_option_order


class PollingOrderMonitor:
    """Poll-based order monitor - checks every N seconds for new orders."""
    
    def __init__(self, client: SmartAPIClient, check_interval=1):
        """
        Initialize polling monitor.
        
        Args:
            client: SmartAPIClient instance
            check_interval: Seconds between checks (default: 1)
        """
        self.client = client
        self.check_interval = check_interval
        self.known_order_ids = set()
        self._initialize_known_orders()
    
    def _initialize_known_orders(self):
        """Load existing orders to avoid treating them as new."""
        try:
            order_book = self.client.get_order_book()
            if order_book and 'data' in order_book and order_book['data']:
                self.known_order_ids = {
                    order.get('orderid') for order in order_book['data']
                }
                print(f"✅ Initialized with {len(self.known_order_ids)} existing orders")
        except Exception as e:
            print(f"Error initializing known orders: {e}")
    
    def check_for_new_orders(self):
        """Check order book for new orders."""
        try:
            order_book = self.client.get_order_book()
            if not order_book or 'data' not in order_book or not order_book['data']:
                return []
            
            new_orders = []
            for order in order_book['data']:
                order_id = order.get('orderid')
                
                if order_id and order_id not in self.known_order_ids:
                    self.known_order_ids.add(order_id)
                    new_orders.append(order)
            
            return new_orders
        except Exception as e:
            print(f"Error checking for new orders: {e}")
            return []
    
    def on_new_order(self, order):
        """
        Handler called when a new order is detected.
        Override this method for custom behavior.
        
        Args:
            order: Order dictionary
        """
        print("\n" + "🔔 " * 30)
        print(f"NEW ORDER DETECTED AT {datetime.now()}")
        print("🔔 " * 30 + "\n")
        display_option_order(order)
    
    def start(self):
        """Start monitoring for new orders."""
        print("="*100)
        print("POLLING ORDER MONITOR STARTED")
        print("="*100)
        print(f"Check interval: {self.check_interval} seconds")
        print(f"Monitoring account: {self.client.client_id}")
        print("Press Ctrl+C to stop")
        print("="*100 + "\n")
        
        try:
            while True:
                new_orders = self.check_for_new_orders()
                
                for order in new_orders:
                    self.on_new_order(order)
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user.")


def main():
    """Example usage."""
    client = SmartAPIClient()
    monitor = PollingOrderMonitor(client, check_interval=3)
    monitor.start()


if __name__ == "__main__":
    main()
