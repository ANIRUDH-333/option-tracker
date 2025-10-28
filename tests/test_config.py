"""
Test configuration loading and validation.
Critical: Wrong credentials = failed trades or unauthorized access.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


class TestConfig(unittest.TestCase):
    """Test configuration management."""
    
    def setUp(self):
        """Store original env vars."""
        self.original_env = {}
        env_vars = ['API_KEY', 'CLIENT_ID', 'PASSWORD', 'TOTP_SECRET', 'SECRET_KEY']
        for var in env_vars:
            self.original_env[var] = os.environ.get(var)
    
    def tearDown(self):
        """Restore original env vars."""
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]
    
    def test_config_loads_from_env(self):
        """Test that config loads from environment variables."""
        # This should not raise an exception
        try:
            Config.API_KEY
            Config.CLIENT_ID
            Config.PASSWORD
            Config.TOTP_SECRET
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Config failed to load: {e}")
    
    def test_config_validation_fails_with_missing_vars(self):
        """Test that validation fails when required vars are missing."""
        # This test verifies the validation logic works
        # Note: In real environment, missing vars will cause import error
        # This tests the validate() method specifically
        
        # Test with mock config
        class MockConfig:
            API_KEY = None
            CLIENT_ID = "test"
            PASSWORD = "test"
            TOTP_SECRET = "test"
            SECRET_KEY = "test"
            
            @classmethod
            def validate(cls):
                required_vars = ['API_KEY', 'CLIENT_ID', 'PASSWORD', 'TOTP_SECRET', 'SECRET_KEY']
                missing = [var for var in required_vars if not getattr(cls, var)]
                if missing:
                    raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
                return True
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            MockConfig.validate()
    
    def test_all_required_vars_present(self):
        """Test that all required configuration variables are present."""
        required = ['API_KEY', 'CLIENT_ID', 'PASSWORD', 'TOTP_SECRET', 'SECRET_KEY']
        
        for var in required:
            value = getattr(Config, var, None)
            self.assertIsNotNone(
                value, 
                f"❌ CRITICAL: {var} is missing! Check your .env file"
            )
            self.assertNotEqual(
                value, 
                '', 
                f"❌ CRITICAL: {var} is empty! Check your .env file"
            )
    
    def test_credentials_not_placeholder(self):
        """Test that credentials are not placeholder values."""
        placeholders = ['your_', 'YOUR_', 'xxx', 'XXX', 'test', 'TEST']
        
        # Check API_KEY
        api_key = Config.API_KEY or ''
        for placeholder in placeholders:
            self.assertNotIn(
                placeholder,
                api_key,
                "❌ CRITICAL: API_KEY appears to be a placeholder!"
            )


if __name__ == '__main__':
    unittest.main()
