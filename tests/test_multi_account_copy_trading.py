"""
Unit tests for multi-account copy trading system.
Run these tests before using the system with real accounts.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multi_account_config import AccountConfig, MultiAccountConfig
from multi_account_copy_trader import CopyTradingSettings, OrderTracker


class TestAccountConfig(unittest.TestCase):
    """Test account configuration."""
    
    def test_account_config_creation(self):
        """Test creating account config."""
        account = AccountConfig(
            name="Test",
            api_key="test_key",
            client_id="TEST123",
            password="password",
            totp_secret="secret",
            secret_key="secret_key"
        )
        
        self.assertEqual(account.name, "Test")
        self.assertEqual(account.client_id, "TEST123")
    
    def test_account_validation_success(self):
        """Test validation with complete config."""
        account = AccountConfig(
            name="Test",
            api_key="test_key",
            client_id="TEST123",
            password="password",
            totp_secret="secret",
            secret_key="secret_key"
        )
        
        self.assertTrue(account.validate())
    
    def test_account_validation_failure(self):
        """Test validation with incomplete config."""
        account = AccountConfig(
            name="Test",
            api_key="",
            client_id="TEST123",
            password="",
            totp_secret="secret",
            secret_key="secret_key"
        )
        
        with self.assertRaises(ValueError):
            account.validate()
    
    def test_account_to_dict(self):
        """Test converting account to dict."""
        account = AccountConfig(
            name="Test",
            api_key="test_key",
            client_id="TEST123",
            password="password",
            totp_secret="secret",
            secret_key="secret_key"
        )
        
        data = account.to_dict()
        self.assertEqual(data['name'], "Test")
        self.assertTrue(data['has_api_key'])
        # Sensitive data should not be in dict
        self.assertNotIn('api_key', data)
        self.assertNotIn('password', data)


class TestCopyTradingSettings(unittest.TestCase):
    """Test copy trading settings."""
    
    def test_default_settings(self):
        """Test default settings initialization."""
        settings = CopyTradingSettings()
        
        self.assertTrue(settings.copy_all_orders)
        self.assertTrue(settings.copy_market_orders)
        self.assertEqual(settings.quantity_multiplier, 1.0)
        self.assertFalse(settings.dry_run)
    
    def test_should_copy_order_allowed_symbol(self):
        """Test order filtering with allowed symbols."""
        settings = CopyTradingSettings()
        settings.copy_all_orders = False
        settings.allowed_symbols = ['NIFTY', 'BANKNIFTY']
        
        order = {'tradingsymbol': 'NIFTY', 'ordertype': 'MARKET'}
        should_copy, reason = settings.should_copy_order(order)
        self.assertTrue(should_copy)
        
        order = {'tradingsymbol': 'FINNIFTY', 'ordertype': 'MARKET'}
        should_copy, reason = settings.should_copy_order(order)
        self.assertFalse(should_copy)
    
    def test_should_copy_order_blocked_symbol(self):
        """Test order filtering with blocked symbols."""
        settings = CopyTradingSettings()
        settings.blocked_symbols = ['FINNIFTY']
        
        order = {'tradingsymbol': 'FINNIFTY', 'ordertype': 'MARKET'}
        should_copy, reason = settings.should_copy_order(order)
        self.assertFalse(should_copy)
        self.assertIn('blocked', reason.lower())
    
    def test_should_copy_order_types(self):
        """Test filtering by order type."""
        settings = CopyTradingSettings()
        settings.copy_market_orders = False
        
        order = {'tradingsymbol': 'NIFTY', 'ordertype': 'MARKET'}
        should_copy, reason = settings.should_copy_order(order)
        self.assertFalse(should_copy)
        
        settings.copy_limit_orders = True
        order = {'tradingsymbol': 'NIFTY', 'ordertype': 'LIMIT'}
        should_copy, reason = settings.should_copy_order(order)
        self.assertTrue(should_copy)
    
    def test_calculate_follower_quantity_multiplier(self):
        """Test quantity calculation with multiplier."""
        settings = CopyTradingSettings()
        settings.quantity_multiplier = 0.5
        
        follower_qty = settings.calculate_follower_quantity(100)
        self.assertEqual(follower_qty, 50)
    
    def test_calculate_follower_quantity_fixed(self):
        """Test quantity calculation with fixed quantity."""
        settings = CopyTradingSettings()
        settings.use_fixed_quantity = True
        settings.fixed_quantity = 25
        
        follower_qty = settings.calculate_follower_quantity(100)
        self.assertEqual(follower_qty, 25)


class TestOrderTracker(unittest.TestCase):
    """Test order tracking."""
    
    def test_is_new_order(self):
        """Test new order detection."""
        tracker = OrderTracker()
        
        self.assertTrue(tracker.is_new_order('ORDER1'))
        self.assertFalse(tracker.is_new_order('ORDER1'))  # Already seen
        self.assertTrue(tracker.is_new_order('ORDER2'))
    
    def test_record_copy_success(self):
        """Test recording successful copy."""
        tracker = OrderTracker()
        
        master_order = {
            'orderid': 'M123',
            'tradingsymbol': 'NIFTY',
            'transactiontype': 'BUY',
            'quantity': '50',
            'price': '18000'
        }
        
        response = {
            'status': True,
            'data': {'orderid': 'F456'}
        }
        
        tracker.record_copy(master_order, 'Follower1', True, response)
        
        self.assertEqual(len(tracker.copy_records), 1)
        self.assertEqual(tracker.copy_records[0]['success'], True)
        self.assertEqual(tracker.copy_records[0]['follower_order_id'], 'F456')
    
    def test_record_copy_failure(self):
        """Test recording failed copy."""
        tracker = OrderTracker()
        
        master_order = {
            'orderid': 'M123',
            'tradingsymbol': 'NIFTY',
            'transactiontype': 'BUY',
            'quantity': '50',
            'price': '18000'
        }
        
        tracker.record_copy(master_order, 'Follower1', False, error='Rate limit exceeded')
        
        self.assertEqual(len(tracker.copy_records), 1)
        self.assertEqual(len(tracker.failed_copies), 1)
        self.assertIn('Rate limit', tracker.failed_copies[0]['error'])
    
    def test_get_statistics(self):
        """Test statistics calculation."""
        tracker = OrderTracker()
        
        master_order = {
            'orderid': 'M123',
            'tradingsymbol': 'NIFTY',
            'transactiontype': 'BUY',
            'quantity': '50',
            'price': '18000'
        }
        
        # Record 3 successful and 1 failed
        for i in range(3):
            tracker.record_copy(master_order, f'Follower{i}', True, {'data': {'orderid': f'F{i}'}})
        
        tracker.record_copy(master_order, 'Follower3', False, error='Failed')
        
        stats = tracker.get_statistics()
        
        self.assertEqual(stats['total_copies'], 4)
        self.assertEqual(stats['successful'], 3)
        self.assertEqual(stats['failed'], 1)
        self.assertEqual(stats['success_rate'], 75.0)


class TestOrderParameters(unittest.TestCase):
    """Test order parameter construction."""
    
    def test_order_params_market_order(self):
        """Test building params for market order."""
        master_order = {
            'variety': 'NORMAL',
            'tradingsymbol': 'NIFTY23FEB18000CE',
            'symboltoken': '12345',
            'transactiontype': 'BUY',
            'exchange': 'NFO',
            'ordertype': 'MARKET',
            'producttype': 'INTRADAY',
            'duration': 'DAY',
            'quantity': '50',
            'price': '0',
            'status': 'complete'
        }
        
        # Build params as the copy trader would
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
            'quantity': str(master_order.get('quantity')),
        }
        
        self.assertEqual(order_params['ordertype'], 'MARKET')
        self.assertEqual(order_params['price'], '0')
        self.assertEqual(order_params['quantity'], '50')
    
    def test_order_params_limit_order(self):
        """Test building params for limit order."""
        master_order = {
            'variety': 'NORMAL',
            'tradingsymbol': 'NIFTY23FEB18000CE',
            'symboltoken': '12345',
            'transactiontype': 'SELL',
            'exchange': 'NFO',
            'ordertype': 'LIMIT',
            'producttype': 'INTRADAY',
            'duration': 'DAY',
            'quantity': '25',
            'price': '150.50',
            'status': 'complete'
        }
        
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
            'quantity': str(master_order.get('quantity')),
        }
        
        self.assertEqual(order_params['ordertype'], 'LIMIT')
        self.assertEqual(order_params['price'], '150.50')
        self.assertEqual(order_params['transactiontype'], 'SELL')


def run_all_tests():
    """Run all test suites."""
    print("\n" + "="*100)
    print("RUNNING MULTI-ACCOUNT COPY TRADING TESTS")
    print("="*100 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAccountConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestCopyTradingSettings))
    suite.addTests(loader.loadTestsFromTestCase(TestOrderTracker))
    suite.addTests(loader.loadTestsFromTestCase(TestOrderParameters))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*100)
    print("TEST SUMMARY")
    print("="*100)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*100 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
