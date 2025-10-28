"""
Multi-account configuration for copy trading.
Supports one master account and multiple follower accounts.
"""
import os
import json
from typing import Dict, List

# Try to load environment variables from .env file (for local development)
# In production, environment variables should be set directly in the deployment platform
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not available (this is fine in production)
    pass


class AccountConfig:
    """Configuration for a single Angel One account."""
    
    def __init__(self, name: str, api_key: str, client_id: str, 
                 password: str, totp_secret: str, secret_key: str):
        """
        Initialize account configuration.
        
        Args:
            name: Friendly name for the account (e.g., "Master", "Follower1")
            api_key: Angel One API key
            client_id: Angel One client ID
            password: Account password
            totp_secret: TOTP secret for 2FA
            secret_key: Secret key
        """
        self.name = name
        self.api_key = api_key
        self.client_id = client_id
        self.password = password
        self.totp_secret = totp_secret
        self.secret_key = secret_key
    
    def validate(self) -> bool:
        """Validate that all required fields are present."""
        required_fields = [
            self.api_key, self.client_id, self.password, 
            self.totp_secret, self.secret_key
        ]
        if not all(required_fields):
            missing = []
            if not self.api_key: missing.append("api_key")
            if not self.client_id: missing.append("client_id")
            if not self.password: missing.append("password")
            if not self.totp_secret: missing.append("totp_secret")
            if not self.secret_key: missing.append("secret_key")
            raise ValueError(f"Account '{self.name}' missing: {', '.join(missing)}")
        return True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary (for saving/logging - without sensitive data)."""
        return {
            'name': self.name,
            'client_id': self.client_id,
            'has_api_key': bool(self.api_key),
            'has_password': bool(self.password),
            'has_totp_secret': bool(self.totp_secret),
            'has_secret_key': bool(self.secret_key),
        }


class MultiAccountConfig:
    """Configuration manager for multi-account copy trading."""
    
    def __init__(self):
        """Initialize multi-account configuration."""
        self.master_account: AccountConfig = None
        self.follower_accounts: List[AccountConfig] = []
        self._load_from_env()
    
    def _load_from_env(self):
        """Load account configurations from environment variables."""
        # Load master account (default account from .env)
        self.master_account = AccountConfig(
            name="Master",
            api_key=os.getenv('API_KEY'),
            client_id=os.getenv('CLIENT_ID'),
            password=os.getenv('PASSWORD'),
            totp_secret=os.getenv('TOTP_SECRET'),
            secret_key=os.getenv('SECRET_KEY')
        )
        
        # Load follower accounts
        # Format: FOLLOWER_1_API_KEY, FOLLOWER_1_CLIENT_ID, etc.
        follower_count = 1
        while True:
            prefix = f'FOLLOWER_{follower_count}_'
            api_key = os.getenv(f'{prefix}API_KEY')
            
            # Stop when no more followers found
            if not api_key:
                break
            
            follower = AccountConfig(
                name=f"Follower{follower_count}",
                api_key=api_key,
                client_id=os.getenv(f'{prefix}CLIENT_ID'),
                password=os.getenv(f'{prefix}PASSWORD'),
                totp_secret=os.getenv(f'{prefix}TOTP_SECRET'),
                secret_key=os.getenv(f'{prefix}SECRET_KEY')
            )
            
            self.follower_accounts.append(follower)
            follower_count += 1
    
    def load_from_file(self, filepath: str):
        """
        Load account configurations from a JSON file.
        WARNING: Store credentials securely! Use environment variables in production.
        
        Args:
            filepath: Path to JSON configuration file
        """
        try:
            with open(filepath, 'r') as f:
                config_data = json.load(f)
            
            # Load master account
            if 'master' in config_data:
                master = config_data['master']
                self.master_account = AccountConfig(
                    name="Master",
                    api_key=master.get('api_key', ''),
                    client_id=master.get('client_id', ''),
                    password=master.get('password', ''),
                    totp_secret=master.get('totp_secret', ''),
                    secret_key=master.get('secret_key', '')
                )
            
            # Load follower accounts
            if 'followers' in config_data:
                self.follower_accounts = []
                for idx, follower in enumerate(config_data['followers'], 1):
                    account = AccountConfig(
                        name=follower.get('name', f'Follower{idx}'),
                        api_key=follower.get('api_key', ''),
                        client_id=follower.get('client_id', ''),
                        password=follower.get('password', ''),
                        totp_secret=follower.get('totp_secret', ''),
                        secret_key=follower.get('secret_key', '')
                    )
                    self.follower_accounts.append(account)
            
            print(f"✅ Loaded configuration from {filepath}")
            print(f"   Master: {self.master_account.client_id}")
            print(f"   Followers: {len(self.follower_accounts)}")
            
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {filepath}")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in configuration file: {e}")
            raise
    
    def validate(self) -> bool:
        """Validate all account configurations."""
        try:
            # Validate master account
            if not self.master_account:
                raise ValueError("Master account not configured")
            self.master_account.validate()
            
            # Validate follower accounts
            if not self.follower_accounts:
                print("⚠️  Warning: No follower accounts configured")
            
            for follower in self.follower_accounts:
                follower.validate()
            
            return True
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            raise
    
    def get_summary(self) -> Dict:
        """Get a summary of the configuration (safe for logging)."""
        return {
            'master': self.master_account.to_dict() if self.master_account else None,
            'followers': [f.to_dict() for f in self.follower_accounts],
            'total_followers': len(self.follower_accounts)
        }
    
    def print_summary(self):
        """Print a formatted summary of the configuration."""
        print("\n" + "="*100)
        print("MULTI-ACCOUNT COPY TRADING CONFIGURATION")
        print("="*100)
        
        if self.master_account:
            print(f"\n📊 Master Account:")
            print(f"   Name: {self.master_account.name}")
            print(f"   Client ID: {self.master_account.client_id}")
        
        if self.follower_accounts:
            print(f"\n👥 Follower Accounts ({len(self.follower_accounts)}):")
            for idx, follower in enumerate(self.follower_accounts, 1):
                print(f"   {idx}. {follower.name} (Client ID: {follower.client_id})")
        else:
            print(f"\n⚠️  No follower accounts configured")
        
        print("\n" + "="*100 + "\n")


# Example .env.multi_account template
ENV_TEMPLATE = """
# Master Account (the account to copy FROM)
API_KEY=your_master_api_key
CLIENT_ID=your_master_client_id
PASSWORD=your_master_password
TOTP_SECRET=your_master_totp_secret
SECRET_KEY=your_master_secret_key

# Follower Account 1 (account to copy TO)
FOLLOWER_1_API_KEY=follower1_api_key
FOLLOWER_1_CLIENT_ID=follower1_client_id
FOLLOWER_1_PASSWORD=follower1_password
FOLLOWER_1_TOTP_SECRET=follower1_totp_secret
FOLLOWER_1_SECRET_KEY=follower1_secret_key

# Follower Account 2 (account to copy TO)
FOLLOWER_2_API_KEY=follower2_api_key
FOLLOWER_2_CLIENT_ID=follower2_client_id
FOLLOWER_2_PASSWORD=follower2_password
FOLLOWER_2_TOTP_SECRET=follower2_totp_secret
FOLLOWER_2_SECRET_KEY=follower2_secret_key

# Add more follower accounts as needed (FOLLOWER_3_, FOLLOWER_4_, etc.)
"""


if __name__ == "__main__":
    # Test configuration loading
    config = MultiAccountConfig()
    config.print_summary()
    
    # Optionally save template
    print("Example .env template for multi-account setup:")
    print(ENV_TEMPLATE)
