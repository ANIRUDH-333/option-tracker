"""
WebSocket-based real-time order monitoring for copy trading.
Uses SmartAPI WebSocket to get instant notifications when orders are placed.
"""
import json
from datetime import datetime
from SmartApi import SmartWebSocketV2
from smartapi_client import SmartAPIClient
from display import display_option_order
from config import Config


class OrderMonitor:
    """Real-time order monitor using WebSocket."""
    
    def __init__(self, client: SmartAPIClient):
        """
        Initialize order monitor.
        
        Args:
            client: SmartAPIClient instance
        """
        self.client = client
        self.feed_token = client.feed_token
        self.api_key = Config.API_KEY
        self.client_code = Config.CLIENT_ID
        
        # Store last known orders to detect new ones
        self.known_order_ids = set()
        self._initialize_known_orders()
        
        # WebSocket connection
        self.ws = None
    
    def _initialize_known_orders(self):
        """Load existing orders to avoid treating them as new."""
        try:
            order_book = self.client.get_order_book()
            if order_book and 'data' in order_book and order_book['data']:
                self.known_order_ids = {
                    order.get('orderid') for order in order_book['data']
                }
                print(f"Initialized with {len(self.known_order_ids)} existing orders")
        except Exception as e:
            print(f"Error initializing known orders: {e}")
    
    def on_open(self, wsapp):
        """Callback when WebSocket connection opens."""
        print(f"[{datetime.now()}] WebSocket connection opened")
        print("Monitoring for new orders in real-time...")
        print("="*100 + "\n")
    
    def on_error(self, wsapp, error):
        """Callback when WebSocket error occurs."""
        print(f"[{datetime.now()}] WebSocket error: {error}")
    
    def on_close(self, wsapp):
        """Callback when WebSocket connection closes."""
        print(f"[{datetime.now()}] WebSocket connection closed")
    
    def on_data(self, wsapp, message):
        """
        Callback when data is received from WebSocket.
        This is where you'll detect new orders instantly.
        """
        try:
            # Parse the message
            data = json.loads(message) if isinstance(message, str) else message
            
            # Check if it's an order update
            if self._is_order_update(data):
                self._check_for_new_orders()
        except Exception as e:
            print(f"Error processing WebSocket data: {e}")
    
    def _is_order_update(self, data):
        """
        Determine if the WebSocket message is an order-related update.
        Adjust this based on SmartAPI's actual message format.
        """
        # This needs to be adjusted based on actual SmartAPI WebSocket message format
        # Common indicators: action type, message type, etc.
        return True  # For now, check on every message
    
    def _check_for_new_orders(self):
        """Check order book for new orders and process them."""
        try:
            order_book = self.client.get_order_book()
            if not order_book or 'data' not in order_book or not order_book['data']:
                return
            
            # Find new orders
            for order in order_book['data']:
                order_id = order.get('orderid')
                
                if order_id and order_id not in self.known_order_ids:
                    # NEW ORDER DETECTED!
                    self.known_order_ids.add(order_id)
                    self.on_new_order(order)
        except Exception as e:
            print(f"Error checking for new orders: {e}")
    
    def on_new_order(self, order):
        """
        Handler for new order detection.
        THIS IS WHERE YOU'LL IMPLEMENT COPY TRADING LOGIC.
        
        Args:
            order: Order dictionary from orderBook API
        """
        print("\n" + "🔔 " * 30)
        print(f"NEW ORDER DETECTED AT {datetime.now()}")
        print("🔔 " * 30 + "\n")
        
        # Display order details
        display_option_order(order)
        
        # TODO: Implement copy trading logic here
        # self.place_mirror_order(order)
    
    def place_mirror_order(self, original_order):
        """
        Place a mirror order in another account.
        
        Args:
            original_order: The original order to copy
        """
        print(f"[COPY TRADE] Placing mirror order for {original_order.get('tradingsymbol')}")
        
        # TODO: Implement with second account's SmartAPI client
        # mirror_order_params = {
        #     'tradingsymbol': original_order.get('tradingsymbol'),
        #     'symboltoken': original_order.get('symboltoken'),
        #     'transactiontype': original_order.get('transactiontype'),
        #     'exchange': original_order.get('exchange'),
        #     'ordertype': original_order.get('ordertype'),
        #     'producttype': original_order.get('producttype'),
        #     'quantity': original_order.get('quantity'),
        #     'price': original_order.get('price'),
        # }
        # 
        # second_account_client.place_order(mirror_order_params)
        pass
    
    def start_monitoring(self):
        """Start WebSocket monitoring (Method 1: Using SmartWebSocket)."""
        try:
            # Initialize WebSocket
            self.ws = SmartWebSocketV2(
                auth_token=self.feed_token,
                api_key=self.api_key,
                client_code=self.client_code,
                feed_token=self.feed_token
            )
            
            # Set callbacks
            self.ws.on_open = self.on_open
            self.ws.on_data = self.on_data
            self.ws.on_error = self.on_error
            self.ws.on_close = self.on_close
            
            # Connect and start listening
            self.ws.connect()
            
        except Exception as e:
            print(f"Error starting WebSocket monitor: {e}")
            print("\nFalling back to polling method...")
            self.start_polling_monitor()
    
    def start_polling_monitor(self, interval=3):
        """
        Fallback: Poll-based monitoring (checks every few seconds).
        Less ideal but more reliable than long intervals.
        
        Args:
            interval: Seconds between checks (default: 3)
        """
        import time
        
        print(f"Starting polling monitor (checking every {interval} seconds)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self._check_for_new_orders()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
