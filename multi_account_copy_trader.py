"""
Multi-Account Copy Trading Manager
Monitors master account and executes trades in multiple follower accounts.
"""
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from multi_account_config import MultiAccountConfig
from multi_account_client import ClientManager, MultiAccountClient


class CopyTradingSettings:
    """Settings for copy trading behavior."""
    
    def __init__(self):
        """Initialize default settings."""
        # Order filtering
        self.copy_all_orders = True  # If False, only copy specific symbols
        self.allowed_symbols = []  # Empty = all symbols allowed
        self.blocked_symbols = []  # Symbols to never copy
        
        # Quantity management
        self.use_fixed_quantity = False  # Use same quantity for all followers
        self.fixed_quantity = None  # Fixed quantity if use_fixed_quantity=True
        self.quantity_multiplier = 1.0  # Multiply master quantity by this factor
        
        # Risk management
        self.max_order_value = None  # Maximum value per order (None = no limit)
        self.daily_loss_limit = None  # Stop copying if daily loss exceeds this
        
        # Order types
        self.copy_market_orders = True
        self.copy_limit_orders = True
        self.copy_stop_orders = True
        
        # Safety features
        self.dry_run = False  # If True, simulate orders without placing them
        self.require_confirmation = False  # If True, ask before each trade
        self.log_all_actions = True  # Log every decision and action
    
    def should_copy_order(self, order: Dict) -> tuple[bool, str]:
        """
        Determine if an order should be copied based on settings.
        
        Args:
            order: Order dictionary from master account
            
        Returns:
            Tuple of (should_copy: bool, reason: str)
        """
        symbol = order.get('tradingsymbol', '')
        order_type = order.get('ordertype', '').upper()
        
        # Check blocked symbols
        if symbol in self.blocked_symbols:
            return False, f"Symbol {symbol} is blocked"
        
        # Check allowed symbols
        if not self.copy_all_orders and symbol not in self.allowed_symbols:
            return False, f"Symbol {symbol} not in allowed list"
        
        # Check order type
        if order_type == 'MARKET' and not self.copy_market_orders:
            return False, "Market orders disabled"
        if order_type == 'LIMIT' and not self.copy_limit_orders:
            return False, "Limit orders disabled"
        if order_type in ['STOPLOSS', 'STOPLOSS_MARKET'] and not self.copy_stop_orders:
            return False, "Stop orders disabled"
        
        return True, "Order passes all filters"
    
    def calculate_follower_quantity(self, master_quantity: int, 
                                    follower_name: str = None) -> int:
        """
        Calculate the quantity for a follower account.
        
        Args:
            master_quantity: Quantity from master account
            follower_name: Name of follower account (for account-specific rules)
            
        Returns:
            Calculated quantity for follower
        """
        if self.use_fixed_quantity and self.fixed_quantity:
            return self.fixed_quantity
        
        return int(master_quantity * self.quantity_multiplier)


class OrderTracker:
    """Tracks orders and their copy status."""
    
    def __init__(self):
        """Initialize order tracker."""
        self.known_master_orders = set()  # Order IDs seen from master
        self.copy_records = []  # List of copy attempts
        self.failed_copies = []  # Failed copy attempts for retry
    
    def is_new_order(self, order_id: str) -> bool:
        """Check if this is a new order we haven't seen."""
        if order_id in self.known_master_orders:
            return False
        self.known_master_orders.add(order_id)
        return True
    
    def record_copy(self, master_order: Dict, follower_name: str, 
                   success: bool, response: Optional[Dict] = None,
                   error: Optional[str] = None):
        """
        Record a copy trading attempt.
        
        Args:
            master_order: Original order from master
            follower_name: Name of follower account
            success: Whether copy was successful
            response: API response if successful
            error: Error message if failed
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'master_order_id': master_order.get('orderid'),
            'symbol': master_order.get('tradingsymbol'),
            'transaction_type': master_order.get('transactiontype'),
            'quantity': master_order.get('quantity'),
            'price': master_order.get('price'),
            'follower': follower_name,
            'success': success,
            'follower_order_id': response.get('data', {}).get('orderid') if response else None,
            'error': error
        }
        
        self.copy_records.append(record)
        
        if not success:
            self.failed_copies.append(record)
    
    def get_statistics(self) -> Dict:
        """Get copy trading statistics."""
        total = len(self.copy_records)
        successful = sum(1 for r in self.copy_records if r['success'])
        failed = total - successful
        
        return {
            'total_copies': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0
        }
    
    def save_to_file(self, filepath: str):
        """Save copy records to JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    'records': self.copy_records,
                    'statistics': self.get_statistics()
                }, f, indent=2)
            print(f"   💾 Records saved to {filepath}")
        except Exception as e:
            print(f"   ⚠️  Failed to save records: {e}")


class MultiAccountCopyTrader:
    """Main copy trading manager for multiple accounts."""
    
    def __init__(self, config: MultiAccountConfig, settings: CopyTradingSettings = None):
        """
        Initialize multi-account copy trader.
        
        Args:
            config: MultiAccountConfig with all account details
            settings: CopyTradingSettings for behavior customization
        """
        self.config = config
        self.settings = settings or CopyTradingSettings()
        self.client_manager = ClientManager()
        self.tracker = OrderTracker()
        
        # Initialize all clients
        self.client_manager.initialize_clients(config)
        
        # Load initial orders to avoid copying old ones
        self._initialize_known_orders()
    
    def _initialize_known_orders(self):
        """Load existing orders from master to avoid treating them as new."""
        try:
            print("📚 Loading existing orders from master account...")
            order_book = self.client_manager.master_client.get_order_book()
            
            if order_book and 'data' in order_book and order_book['data']:
                for order in order_book['data']:
                    order_id = order.get('orderid')
                    if order_id:
                        self.tracker.known_master_orders.add(order_id)
                
                print(f"   ✅ Initialized with {len(self.tracker.known_master_orders)} "
                      f"existing orders\n")
        except Exception as e:
            print(f"   ⚠️  Error loading existing orders: {e}\n")
    
    def check_for_new_orders(self) -> List[Dict]:
        """
        Check master account for new orders.
        
        Returns:
            List of new orders detected
        """
        try:
            order_book = self.client_manager.master_client.get_order_book()
            
            if not order_book or 'data' not in order_book or not order_book['data']:
                return []
            
            new_orders = []
            for order in order_book['data']:
                order_id = order.get('orderid')
                
                if order_id and self.tracker.is_new_order(order_id):
                    # Only process completed orders
                    if order.get('status') == 'complete':
                        new_orders.append(order)
            
            return new_orders
            
        except Exception as e:
            print(f"❌ Error checking for new orders: {e}")
            return []
    
    def copy_order_to_followers(self, master_order: Dict):
        """
        Copy an order from master to all follower accounts.
        
        Args:
            master_order: Order dictionary from master account
        """
        print("\n" + "🔔 " * 40)
        print(f"NEW ORDER DETECTED AT {datetime.now()}")
        print("🔔 " * 40)
        
        # Display order details
        self._display_order(master_order)
        
        # Check if we should copy this order
        should_copy, reason = self.settings.should_copy_order(master_order)
        
        if not should_copy:
            print(f"\n⏭️  Skipping order: {reason}\n")
            print("="*100 + "\n")
            return
        
        print(f"✅ Order approved for copying: {reason}")
        
        # Get active followers
        active_followers = self.client_manager.get_all_active_followers()
        
        if not active_followers:
            print("\n⚠️  No active follower accounts to copy to\n")
            print("="*100 + "\n")
            return
        
        # Dry run check
        if self.settings.dry_run:
            print(f"\n🔍 DRY RUN MODE: Would copy to {len(active_followers)} followers")
            self._display_order_params(master_order)
            print("="*100 + "\n")
            return
        
        # Confirmation check
        if self.settings.require_confirmation:
            response = input(f"\n❓ Copy this order to {len(active_followers)} followers? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("   ⏭️  Skipped by user\n")
                print("="*100 + "\n")
                return
        
        # Copy to each follower
        print(f"\n📤 Copying to {len(active_followers)} follower account(s)...\n")
        
        for follower_client in active_followers:
            self._copy_to_single_follower(master_order, follower_client)
        
        print("\n" + "="*100 + "\n")
    
    def _copy_to_single_follower(self, master_order: Dict, 
                                 follower_client: MultiAccountClient):
        """
        Copy order to a single follower account.
        
        Args:
            master_order: Order from master account
            follower_client: Follower's client instance
        """
        try:
            # Calculate quantity for this follower
            master_qty = int(master_order.get('quantity', 0))
            follower_qty = self.settings.calculate_follower_quantity(
                master_qty, 
                follower_client.account.name
            )
            
            # Prepare order parameters
            order_params = {
                'variety': master_order.get('variety', 'NORMAL'),
                'tradingsymbol': master_order.get('tradingsymbol'),
                'symboltoken': master_order.get('symboltoken'),
                'transactiontype': master_order.get('transactiontype'),
                'exchange': master_order.get('exchange'),
                'ordertype': master_order.get('ordertype'),
                'producttype': master_order.get('producttype'),
                'duration': master_order.get('duration', 'DAY'),
                'price': str(master_order.get('price', '0')),
                'squareoff': '0',
                'stoploss': '0',
                'quantity': str(follower_qty),
            }
            
            # Add trigger price if present
            if master_order.get('triggerprice'):
                order_params['triggerprice'] = str(master_order.get('triggerprice'))
            
            # Place order
            print(f"   📤 {follower_client.account.name}: Placing order...")
            response = follower_client.place_order(order_params)
            
            # Check response
            if response and response.get('status'):
                order_id = response.get('data', {}).get('orderid', 'Unknown')
                print(f"   ✅ {follower_client.account.name}: Success! Order ID: {order_id}")
                self.tracker.record_copy(master_order, follower_client.account.name,
                                        True, response)
            else:
                error_msg = response.get('message', 'Unknown error')
                print(f"   ❌ {follower_client.account.name}: Failed - {error_msg}")
                self.tracker.record_copy(master_order, follower_client.account.name,
                                        False, error=error_msg)
                
        except Exception as e:
            print(f"   ❌ {follower_client.account.name}: Exception - {e}")
            self.tracker.record_copy(master_order, follower_client.account.name,
                                    False, error=str(e))
    
    def _display_order(self, order: Dict):
        """Display order details in a formatted way."""
        print(f"\n📊 Master Account Order Details:")
        print(f"   Symbol: {order.get('tradingsymbol')}")
        print(f"   Type: {order.get('transactiontype')} {order.get('ordertype')}")
        print(f"   Quantity: {order.get('quantity')}")
        print(f"   Price: {order.get('price')}")
        print(f"   Product: {order.get('producttype')}")
        print(f"   Exchange: {order.get('exchange')}")
        print(f"   Status: {order.get('status')}")
        print(f"   Order ID: {order.get('orderid')}")
    
    def _display_order_params(self, order: Dict):
        """Display what would be copied (for dry run)."""
        qty = self.settings.calculate_follower_quantity(int(order.get('quantity', 0)))
        print(f"\n   Symbol: {order.get('tradingsymbol')}")
        print(f"   Type: {order.get('transactiontype')}")
        print(f"   Quantity: {order.get('quantity')} → {qty} (follower)")
        print(f"   Price: {order.get('price')}")
    
    def start_monitoring(self, interval: int = 3):
        """
        Start monitoring master account and copying orders.
        
        Args:
            interval: Seconds between checks (default: 3)
        """
        print("\n" + "="*100)
        print("MULTI-ACCOUNT COPY TRADING STARTED")
        print("="*100)
        print(f"Master Account: {self.config.master_account.client_id}")
        print(f"Follower Accounts: {len(self.client_manager.get_all_active_followers())}")
        print(f"Poll Interval: {interval} seconds")
        print(f"Dry Run Mode: {'ON ⚠️' if self.settings.dry_run else 'OFF'}")
        print("="*100)
        print("\n⏰ Monitoring for new orders... (Press Ctrl+C to stop)\n")
        
        try:
            while True:
                new_orders = self.check_for_new_orders()
                
                for order in new_orders:
                    self.copy_order_to_followers(order)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n" + "="*100)
            print("COPY TRADING STOPPED BY USER")
            print("="*100)
            self._display_summary()
        except Exception as e:
            print(f"\n❌ Error in monitoring loop: {e}")
            self._display_summary()
    
    def _display_summary(self):
        """Display copy trading session summary."""
        stats = self.tracker.get_statistics()
        
        print("\n📊 Session Summary:")
        print(f"   Total Orders Copied: {stats['total_copies']}")
        print(f"   Successful: {stats['successful']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Success Rate: {stats['success_rate']:.1f}%")
        
        # Save records
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f"logs/copy_trading_{timestamp}.json"
        self.tracker.save_to_file(filepath)
        
        print("\n" + "="*100 + "\n")
