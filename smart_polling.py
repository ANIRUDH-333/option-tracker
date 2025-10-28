"""
Smart polling strategy with rate limit protection.
Optimizes API calls while staying within SmartAPI limits.
"""
import time
from datetime import datetime, timedelta
from smartapi_client import SmartAPIClient
from display import display_option_order


class SmartPollingMonitor:
    """
    Intelligent polling monitor with rate limit protection.
    
    SmartAPI Rate Limits (typical):
    - Order Book API: ~10 requests per second (very generous)
    - Recommended: 1-2 requests per second to be safe
    
    Strategies:
    1. Adaptive polling: Fast during market hours, slower otherwise
    2. Exponential backoff on errors
    3. Cache-based detection (only polls when needed)
    """
    
    def __init__(self, client: SmartAPIClient):
        """
        Initialize smart monitor.
        
        Args:
            client: SmartAPIClient instance
        """
        self.client = client
        self.known_order_ids = set()
        self._initialize_known_orders()
        
        # Rate limiting
        self.api_calls_count = 0
        self.api_calls_window_start = time.time()
        self.max_calls_per_minute = 10  # Conservative: 10 calls/minute (6 seconds between calls)
        
        # Adaptive polling intervals
        self.market_hours_interval = 6  # 6 seconds during market hours (10 calls/min - SAFE)
        self.off_hours_interval = 60    # 60 seconds outside market hours
        self.current_interval = self.market_hours_interval
        
        # Rate limit backoff
        self.consecutive_rate_limits = 0
        self.backoff_until = None
    
    def _initialize_known_orders(self):
        """Load existing orders to avoid treating them as new."""
        max_retries = 3
        retry_delay = 10  # Start with 10 seconds
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    wait_time = retry_delay * attempt
                    print(f"🔄 Retrying initialization in {wait_time}s (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                
                order_book = self.client.get_order_book()
                if order_book and 'data' in order_book:
                    order_data = order_book['data']
                    if order_data:  # Check if data is not None and not empty
                        self.known_order_ids = {
                            order.get('orderid') for order in order_data
                        }
                        print(f"✅ Initialized with {len(self.known_order_ids)} existing orders")
                    else:
                        print("✅ Initialized with 0 existing orders (no orders placed yet)")
                return  # Success!
                
            except Exception as e:
                error_msg = str(e).lower()
                if 'rate' in error_msg or 'access denied' in error_msg:
                    if attempt < max_retries - 1:
                        print(f"⚠️  Rate limit during initialization (attempt {attempt + 1}/{max_retries})")
                        continue
                    else:
                        print(f"⚠️  Could not initialize known orders after {max_retries} attempts")
                        print(f"    Will start monitoring anyway, but may detect old orders as new")
                        self.known_order_ids = set()
                else:
                    print(f"Error initializing known orders: {e}")
                    self.known_order_ids = set()
    
    def _is_market_hours(self):
        """
        Check if current time is within market hours.
        NSE: 9:15 AM - 3:30 PM IST (Mon-Fri)
        """
        now = datetime.now()
        
        # Skip weekends
        if now.weekday() >= 5:  # Saturday=5, Sunday=6
            return False
        
        # Check time
        market_open = now.replace(hour=9, minute=15, second=0)
        market_close = now.replace(hour=15, minute=30, second=0)
        
        return market_open <= now <= market_close
    
    def _check_rate_limit(self):
        """
        Check and enforce rate limits.
        Returns True if we can make a call, False if we should wait.
        """
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.api_calls_window_start >= 60:
            self.api_calls_count = 0
            self.api_calls_window_start = current_time
        
        # Check if we've hit the limit
        if self.api_calls_count >= self.max_calls_per_minute:
            wait_time = 60 - (current_time - self.api_calls_window_start)
            if wait_time > 0:
                print(f"⚠️  Rate limit reached ({self.api_calls_count}/{self.max_calls_per_minute}). Waiting {wait_time:.1f}s...")
                time.sleep(wait_time + 1)  # Wait until next minute + 1 second buffer
                self.api_calls_count = 0
                self.api_calls_window_start = time.time()
        
        return True
    
    def _adaptive_interval(self):
        """Get polling interval based on market hours."""
        if self._is_market_hours():
            return self.market_hours_interval
        else:
            return self.off_hours_interval
    
    def check_for_new_orders(self):
        """Check order book for new orders with rate limiting."""
        # Check if we're in backoff period
        if self.backoff_until and time.time() < self.backoff_until:
            remaining = int(self.backoff_until - time.time())
            print(f"⏸️  In backoff period. Waiting {remaining}s...")
            return []
        
        # Check rate limit first
        if not self._check_rate_limit():
            return []
        
        try:
            # Make API call
            order_book = self.client.get_order_book()
            self.api_calls_count += 1
            
            # Reset consecutive rate limits on success
            self.consecutive_rate_limits = 0
            self.backoff_until = None
            
            if not order_book or 'data' not in order_book:
                return []
            
            order_data = order_book['data']
            if not order_data:  # None or empty list
                return []
            
            # Find new orders
            new_orders = []
            for order in order_data:
                order_id = order.get('orderid')
                
                if order_id and order_id not in self.known_order_ids:
                    self.known_order_ids.add(order_id)
                    new_orders.append(order)
            print(new_orders)
            return new_orders
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'rate' in error_msg or 'access denied' in error_msg:
                self.consecutive_rate_limits += 1
                
                # Exponential backoff: 60s, 120s, 240s
                backoff_time = min(60 * (2 ** (self.consecutive_rate_limits - 1)), 300)  # Max 5 minutes
                self.backoff_until = time.time() + backoff_time
                
                print(f"⚠️  Rate limit hit! (attempt {self.consecutive_rate_limits})")
                print(f"   🔄 Backing off for {backoff_time} seconds...")
                print(f"   💡 TIP: Current polling interval may be too aggressive")
                
                # Reset counters
                self.api_calls_count = 0
                self.api_calls_window_start = time.time()
            else:
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
        """Start monitoring with intelligent polling."""
        print("="*100)
        print("SMART POLLING ORDER MONITOR")
        print("="*100)
        print(f"Rate Limit: {self.max_calls_per_minute} calls/minute (safe limit)")
        print(f"Market Hours Interval: {self.market_hours_interval}s (~{60//self.market_hours_interval} calls/min)")
        print(f"Off Hours Interval: {self.off_hours_interval}s")
        print(f"Monitoring account: {self.client.client_id}")
        print("⚠️  If you see rate limit errors, the monitor will auto-backoff")
        
        # Add startup grace period to avoid residual rate limits
        grace_period = 15
        print(f"\n⏳ Waiting {grace_period}s grace period to clear any residual rate limits...")
        time.sleep(grace_period)
        print("✅ Starting monitoring now!")
        
        print("Press Ctrl+C to stop")
        print("="*100 + "\n")
        
        try:
            while True:
                # Get adaptive interval
                self.current_interval = self._adaptive_interval()
                
                # Show status
                market_status = "🟢 MARKET HOURS" if self._is_market_hours() else "🔴 OFF HOURS"
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {market_status} | "
                      f"Checking... (interval: {self.current_interval}s, "
                      f"API calls this minute: {self.api_calls_count}/{self.max_calls_per_minute})")
                
                # Check for new orders
                new_orders = self.check_for_new_orders()
                
                if new_orders:
                    for order in new_orders:
                        self.on_new_order(order)
                
                # Wait before next check
                time.sleep(self.current_interval)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user.")
            print(f"Total API calls made: {self.api_calls_count}")


def main():
    """Example usage."""
    client = SmartAPIClient()
    monitor = SmartPollingMonitor(client)
    monitor.start()


if __name__ == "__main__":
    main()
