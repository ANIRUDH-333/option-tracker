"""
SmartAPI client initialization and session management.
"""
from datetime import datetime
import pyotp
import time
from SmartApi.smartConnect import SmartConnect
from config import Config


class SmartAPIClient:
    """Wrapper class for SmartAPI connection and session management."""
    
    _instance = None
    _session_initialized = False
    
    def __new__(cls):
        """Singleton pattern to reuse the same client instance."""
        if cls._instance is None:
            cls._instance = super(SmartAPIClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize SmartAPI client with credentials from config."""
        # Only initialize once
        if self._session_initialized:
            print(f"♻️  Reusing existing session (initialized at {self.session_time})")
            return
            
        Config.validate()
        
        self.api_key = Config.API_KEY
        self.client_id = Config.CLIENT_ID
        self.password = Config.PASSWORD
        self.totp_secret = Config.TOTP_SECRET
        
        self.totp = pyotp.TOTP(self.totp_secret)
        self.client = SmartConnect(api_key=self.api_key)
        self._initialize_session()
        self.session_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        SmartAPIClient._session_initialized = True
    
    def _initialize_session(self, max_retries=3):
        """
        Initialize SmartAPI session with retry logic.
        
        Args:
            max_retries: Maximum number of retry attempts
        """
        retry_count = 0
        base_delay = 60  # Start with 60 seconds
        
        while retry_count < max_retries:
            try:
                print(f"🔄 Attempting to initialize session (attempt {retry_count + 1}/{max_retries})...")
                
                session = self.client.generateSession(
                    self.client_id,
                    self.password,
                    self.totp.now()
                )
                self.session_data = session
                self.feed_token = self.client.getfeedToken()
                print(f"✅ Session initialized successfully at {datetime.now()}")
                return session
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if 'access rate' in error_msg or 'access denied' in error_msg:
                    retry_count += 1
                    if retry_count < max_retries:
                        # Exponential backoff: 60s, 120s, 180s
                        wait_time = base_delay * retry_count
                        print(f"⚠️  Rate limit hit! Waiting {wait_time} seconds before retry...")
                        print(f"   💡 TIP: Avoid restarting the script multiple times in quick succession")
                        print(f"   📊 Current retry: {retry_count}/{max_retries}")
                        time.sleep(wait_time)
                    else:
                        print(f"❌ Failed after {max_retries} attempts.")
                        print(f"   ⏰ Please wait 5-10 minutes before trying again.")
                        print(f"   🔍 SmartAPI allows only 3-5 session creations per minute.")
                        raise Exception("Rate limit exceeded. Wait 5-10 minutes and try again.")
                else:
                    print(f"❌ Error initializing session: {e}")
                    raise
    
    def get_order_book(self):
        """Fetch order book data with error handling."""
        try:
            return self.client.orderBook()
        except Exception as e:
            error_msg = str(e).lower()
            # Don't print rate limit errors - let caller handle them
            if 'rate' not in error_msg and 'access denied' not in error_msg:
                print(f"Error fetching order book: {e}")
            # Re-raise rate limit errors so caller knows to back off
            raise
    
    def get_trade_book(self):
        """Fetch trade book data."""
        try:
            return self.client.tradeBook()
        except Exception as e:
            print(f"Error fetching trade book: {e}")
            return None
