"""
Multi-account SmartAPI client manager.
Handles creation and management of multiple SmartAPI client instances.
"""
import time
from typing import Dict, List
from datetime import datetime
import pyotp
from SmartApi.smartConnect import SmartConnect
from multi_account_config import AccountConfig


class MultiAccountClient:
    """Manages multiple SmartAPI client instances."""
    
    def __init__(self, account: AccountConfig):
        """
        Initialize a SmartAPI client for a specific account.
        
        Args:
            account: AccountConfig instance with credentials
        """
        self.account = account
        self.api_key = account.api_key
        self.client_id = account.client_id
        self.password = account.password
        self.totp_secret = account.totp_secret
        
        self.totp = pyotp.TOTP(self.totp_secret)
        self.client = SmartConnect(api_key=self.api_key)
        self.session_data = None
        self.feed_token = None
        self.session_time = None
        self.is_initialized = False
    
    def initialize_session(self, max_retries=3, base_delay=60):
        """
        Initialize SmartAPI session with retry logic.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff
        """
        if self.is_initialized:
            print(f"   ♻️  {self.account.name} already initialized at {self.session_time}")
            return True
        
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print(f"   🔄 Initializing {self.account.name} "
                      f"(attempt {retry_count + 1}/{max_retries})...")
                
                self.session_data = self.client.generateSession(
                    self.client_id,
                    self.password,
                    self.totp.now()
                )
                self.feed_token = self.client.getfeedToken()
                self.session_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.is_initialized = True
                
                print(f"   ✅ {self.account.name} initialized successfully")
                return True
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if 'access rate' in error_msg or 'access denied' in error_msg:
                    retry_count += 1
                    if retry_count < max_retries:
                        wait_time = base_delay * retry_count
                        print(f"   ⚠️  Rate limit hit for {self.account.name}! "
                              f"Waiting {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        print(f"   ❌ {self.account.name} failed after {max_retries} attempts")
                        return False
                else:
                    print(f"   ❌ Error initializing {self.account.name}: {e}")
                    return False
        
        return False
    
    def place_order(self, order_params: Dict):
        """
        Place an order using this client.
        
        Args:
            order_params: Order parameters dictionary
            
        Returns:
            API response dictionary
        """
        if not self.is_initialized:
            raise Exception(f"Client {self.account.name} not initialized")
        
        try:
            response = self.client.placeOrder(order_params)
            return response
        except Exception as e:
            print(f"   ❌ Error placing order in {self.account.name}: {e}")
            raise
    
    def get_order_book(self):
        """Fetch order book data."""
        if not self.is_initialized:
            raise Exception(f"Client {self.account.name} not initialized")
        
        try:
            return self.client.orderBook()
        except Exception as e:
            raise
    
    def get_trade_book(self):
        """Fetch trade book data."""
        if not self.is_initialized:
            raise Exception(f"Client {self.account.name} not initialized")
        
        try:
            return self.client.tradeBook()
        except Exception as e:
            raise
    
    def get_profile(self):
        """Get account profile information."""
        if not self.is_initialized:
            raise Exception(f"Client {self.account.name} not initialized")
        
        try:
            return self.client.getProfile(self.client.refreshToken)
        except Exception as e:
            print(f"   ⚠️  Error fetching profile for {self.account.name}: {e}")
            return None


class ClientManager:
    """Manages all client instances (master + followers)."""
    
    def __init__(self):
        """Initialize client manager."""
        self.master_client: MultiAccountClient = None
        self.follower_clients: List[MultiAccountClient] = []
        self.initialization_delay = 5  # Seconds between client initializations
    
    def initialize_clients(self, config):
        """
        Initialize all clients from configuration.
        
        Args:
            config: MultiAccountConfig instance
        """
        print("\n" + "="*100)
        print("INITIALIZING CLIENTS")
        print("="*100 + "\n")
        
        # Initialize master account
        print("🎯 Master Account:")
        self.master_client = MultiAccountClient(config.master_account)
        if not self.master_client.initialize_session():
            raise Exception("Failed to initialize master account")
        
        # Wait before initializing followers to avoid rate limits
        if config.follower_accounts:
            print(f"\n⏱️  Waiting {self.initialization_delay}s before initializing followers...\n")
            time.sleep(self.initialization_delay)
        
        # Initialize follower accounts
        print("👥 Follower Accounts:")
        success_count = 0
        
        for idx, follower_config in enumerate(config.follower_accounts):
            if idx > 0:
                # Add delay between follower initializations
                time.sleep(self.initialization_delay)
            
            follower_client = MultiAccountClient(follower_config)
            if follower_client.initialize_session():
                self.follower_clients.append(follower_client)
                success_count += 1
            else:
                print(f"   ⚠️  Skipping {follower_config.name} due to initialization failure")
        
        print("\n" + "="*100)
        print(f"INITIALIZATION COMPLETE")
        print(f"Master: ✅")
        print(f"Followers: {success_count}/{len(config.follower_accounts)} successful")
        print("="*100 + "\n")
        
        if success_count == 0 and config.follower_accounts:
            print("⚠️  WARNING: No follower accounts initialized successfully!")
            print("   Copy trading will not execute any trades.\n")
    
    def get_all_active_followers(self) -> List[MultiAccountClient]:
        """Get list of successfully initialized follower clients."""
        return [client for client in self.follower_clients if client.is_initialized]
    
    def verify_all_sessions(self):
        """Verify that all sessions are active by fetching profiles."""
        print("\n🔍 Verifying all sessions...")
        
        # Verify master
        master_profile = self.master_client.get_profile()
        if master_profile:
            print(f"   ✅ Master account verified")
        else:
            print(f"   ❌ Master account verification failed")
        
        # Verify followers
        for client in self.follower_clients:
            profile = client.get_profile()
            if profile:
                print(f"   ✅ {client.account.name} verified")
            else:
                print(f"   ❌ {client.account.name} verification failed")
        
        print()
