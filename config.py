"""
Configuration module for SmartAPI credentials and settings.
"""
import os

# Try to load environment variables from .env file (for local development)
# In production, environment variables should be set directly in the deployment platform
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not available (this is fine in production)
    pass


class Config:
    """Configuration class for application settings."""
    
    # SmartAPI credentials
    API_KEY = os.getenv('API_KEY')
    CLIENT_ID = os.getenv('CLIENT_ID')
    PASSWORD = os.getenv('PASSWORD')
    TOTP_SECRET = os.getenv('TOTP_SECRET')
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Polling settings
    POLL_INTERVAL_SECONDS = 120  # 2 minutes
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present."""
        required_vars = ['API_KEY', 'CLIENT_ID', 'PASSWORD', 'TOTP_SECRET', 'SECRET_KEY']
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True
